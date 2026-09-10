#!/usr/bin/env python3
import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo


DEFAULT_GROUP = "Conexión Farcoyo - Rappi"
DEFAULT_DB = (
    "~/Library/Group Containers/group.net.whatsapp.WhatsApp.shared/"
    "ChatStorage.sqlite"
)
DEFAULT_TZ = "America/Mexico_City"
MAC_EPOCH_OFFSET = 978307200


def emit(payload, exit_code=0):
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    raise SystemExit(exit_code)


def error(code, message, **extra):
    payload = {"status": "ERROR", "code": code, "message": message}
    payload.update(extra)
    emit(payload, 1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Export a WhatsApp Desktop group chat read-only."
    )
    parser.add_argument("--group", default=DEFAULT_GROUP)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--tz", default=DEFAULT_TZ)
    return parser.parse_args()


def open_readonly(db_path):
    path = Path(db_path).expanduser()
    if not path.exists():
        error("DB_NOT_FOUND", f"Database does not exist: {path}")
    uri = f"file:{quote(str(path.resolve()), safe='/')}?mode=ro"
    try:
        return sqlite3.connect(uri, uri=True)
    except sqlite3.Error as exc:
        error("SQLITE_OPEN_ERROR", str(exc), db=str(path))


def table_columns(conn, table):
    try:
        rows = conn.execute(f"PRAGMA table_info({quote_identifier(table)})").fetchall()
    except sqlite3.Error as exc:
        error("SQLITE_SCHEMA_ERROR", str(exc), table=table)
    return {row[1] for row in rows}


def quote_identifier(value):
    return '"' + value.replace('"', '""') + '"'


def pick(columns, candidates):
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def require_column(columns, candidates, table, purpose):
    column = pick(columns, candidates)
    if column is None:
        error(
            "COLUMN_NOT_FOUND",
            f"No column found for {purpose} in {table}",
            table=table,
            candidates=candidates,
        )
    return column


def column_expr(alias, column):
    return f"{alias}.{quote_identifier(column)}"


def coalesce_expr(alias, columns, candidates, fallback="NULL"):
    parts = [column_expr(alias, col) for col in candidates if col in columns]
    if not parts:
        return fallback
    if len(parts) == 1:
        return parts[0]
    return "COALESCE(" + ", ".join(parts) + ")"


def has_table(conn, table):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


def resolve_group(conn, group_name):
    if not has_table(conn, "ZWACHATSESSION"):
        error("TABLE_NOT_FOUND", "ZWACHATSESSION table not found")

    chat_columns = table_columns(conn, "ZWACHATSESSION")
    name_col = require_column(
        chat_columns, ["ZPARTNERNAME"], "ZWACHATSESSION", "group name"
    )

    exact_rows = conn.execute(
        f"""
        SELECT Z_PK, {quote_identifier(name_col)}
        FROM ZWACHATSESSION
        WHERE {quote_identifier(name_col)} = ?
        ORDER BY {quote_identifier(name_col)}, Z_PK
        """,
        (group_name,),
    ).fetchall()
    if len(exact_rows) == 1:
        return {"chat_pk": exact_rows[0][0], "name": exact_rows[0][1]}
    if len(exact_rows) > 1:
        multiple_groups(group_name, exact_rows)

    partial_rows = conn.execute(
        f"""
        SELECT Z_PK, {quote_identifier(name_col)}
        FROM ZWACHATSESSION
        WHERE {quote_identifier(name_col)} LIKE ?
        ORDER BY {quote_identifier(name_col)}, Z_PK
        """,
        (f"%{group_name}%",),
    ).fetchall()
    if len(partial_rows) == 1:
        return {"chat_pk": partial_rows[0][0], "name": partial_rows[0][1]}
    if len(partial_rows) > 1:
        multiple_groups(group_name, partial_rows)

    error("GROUP_NOT_FOUND", f"No WhatsApp group matched: {group_name}")


def multiple_groups(group_name, rows):
    emit(
        {
            "status": "ERROR",
            "code": "MULTIPLE_GROUPS",
            "message": "More than one WhatsApp group matched.",
            "group": group_name,
            "matches": [
                {"chat_pk": row[0], "name": row[1]}
                for row in rows
            ],
        },
        1,
    )


def timestamp_mode(raw_value):
    if raw_value is None:
        return "mac"
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return "text"
    if value > 10_000_000_000:
        return "unix_ms"
    if value > 1_500_000_000:
        return "unix"
    return "mac"


def raw_threshold(dt_utc, mode):
    unix_seconds = dt_utc.timestamp()
    if mode == "unix_ms":
        return int(unix_seconds * 1000)
    if mode == "unix":
        return unix_seconds
    if mode == "mac":
        return unix_seconds - MAC_EPOCH_OFFSET
    return dt_utc.isoformat()


def local_time(raw_value, mode, tzinfo):
    if raw_value is None:
        return None
    if mode == "text":
        return str(raw_value)
    value = float(raw_value)
    if mode == "unix_ms":
        unix_seconds = value / 1000
    elif mode == "unix":
        unix_seconds = value
    else:
        unix_seconds = value + MAC_EPOCH_OFFSET
    return (
        datetime.fromtimestamp(unix_seconds, timezone.utc)
        .astimezone(tzinfo)
        .isoformat(timespec="seconds")
    )


def normalize_text(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        for encoding in ("utf-8", "utf-16", "latin-1"):
            try:
                return value.decode(encoding).strip("\x00")
            except UnicodeDecodeError:
                continue
        return value.hex()
    return str(value)


def boolish(value):
    if value is None:
        return False
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes"}
    return bool(value)


def build_joins(message_columns, group_columns, data_columns, media_columns):
    joins = []
    aliases = set()

    group_fk = pick(message_columns, ["ZGROUPMEMBER", "ZMEMBER", "ZGROUPMEMBER1"])
    if group_fk and group_columns:
        joins.append(
            "LEFT JOIN ZWAGROUPMEMBER gm "
            f"ON gm.Z_PK = {column_expr('m', group_fk)}"
        )
        aliases.add("gm")

    data_fk = pick(message_columns, ["ZMESSAGEDATAITEM", "ZDATAITEM"])
    data_message_fk = pick(data_columns, ["ZMESSAGE", "ZMESSAGES", "ZMESSAGE1"])
    if data_columns and data_fk:
        joins.append(
            "LEFT JOIN ZWAMESSAGEDATAITEM di "
            f"ON di.Z_PK = {column_expr('m', data_fk)}"
        )
        aliases.add("di")
    elif data_columns and data_message_fk:
        joins.append(
            "LEFT JOIN ZWAMESSAGEDATAITEM di "
            f"ON {column_expr('di', data_message_fk)} = m.Z_PK"
        )
        aliases.add("di")

    media_fk = pick(message_columns, ["ZMEDIAITEM", "ZMEDIA", "ZMEDIAITEM1"])
    media_message_fk = pick(media_columns, ["ZMESSAGE", "ZMESSAGES", "ZMESSAGE1"])
    if media_columns and media_fk:
        joins.append(
            "LEFT JOIN ZWAMEDIAITEM mi "
            f"ON mi.Z_PK = {column_expr('m', media_fk)}"
        )
        aliases.add("mi")
    elif media_columns and media_message_fk:
        joins.append(
            "LEFT JOIN ZWAMEDIAITEM mi "
            f"ON {column_expr('mi', media_message_fk)} = m.Z_PK"
        )
        aliases.add("mi")

    return joins, aliases


def export_messages(conn, chat, days, tz_name):
    if not has_table(conn, "ZWAMESSAGE"):
        error("TABLE_NOT_FOUND", "ZWAMESSAGE table not found")

    tzinfo = ZoneInfo(tz_name)
    message_columns = table_columns(conn, "ZWAMESSAGE")
    group_columns = table_columns(conn, "ZWAGROUPMEMBER") if has_table(conn, "ZWAGROUPMEMBER") else set()
    data_columns = table_columns(conn, "ZWAMESSAGEDATAITEM") if has_table(conn, "ZWAMESSAGEDATAITEM") else set()
    media_columns = table_columns(conn, "ZWAMEDIAITEM") if has_table(conn, "ZWAMEDIAITEM") else set()

    chat_col = require_column(
        message_columns,
        ["ZCHATSESSION", "ZSESSION", "ZCHAT", "ZCHATSESSION1"],
        "ZWAMESSAGE",
        "chat session",
    )
    date_col = require_column(
        message_columns,
        ["ZMESSAGEDATE", "ZDATE", "ZTIMESTAMP", "ZSENTDATE"],
        "ZWAMESSAGE",
        "message timestamp",
    )
    from_me_col = pick(message_columns, ["ZISFROMME", "ZFROMME", "ZOUTGOING"])
    type_col = pick(message_columns, ["ZMESSAGETYPE", "ZTYPE", "ZKIND"])
    stanza_col = pick(
        message_columns,
        ["ZSTANZAID", "ZMESSAGEID", "ZCLIENTMESSAGEID", "ZID"],
    )

    latest_raw = conn.execute(
        f"""
        SELECT {quote_identifier(date_col)}
        FROM ZWAMESSAGE
        WHERE {quote_identifier(chat_col)} = ?
          AND {quote_identifier(date_col)} IS NOT NULL
        ORDER BY {quote_identifier(date_col)} DESC
        LIMIT 1
        """,
        (chat["chat_pk"],),
    ).fetchone()
    mode = timestamp_mode(latest_raw[0] if latest_raw else None)
    end_local = datetime.now(tzinfo)
    start_local = end_local - timedelta(days=days)
    start_utc = start_local.astimezone(timezone.utc)
    threshold = raw_threshold(start_utc, mode)

    joins, aliases = build_joins(
        message_columns, group_columns, data_columns, media_columns
    )

    sender_parts = []
    if "gm" in aliases:
        sender_parts.append(
            coalesce_expr(
                "gm",
                group_columns,
                [
                    "ZCONTACTNAME",
                    "ZPUSHNAME",
                    "ZFULLNAME",
                    "ZFIRSTNAME",
                    "ZMEMBERJID",
                    "ZJID",
                ],
            )
        )
    sender_parts.append(
        coalesce_expr(
            "m",
            message_columns,
            ["ZFROMJID", "ZAUTHOR", "ZSENDERJID", "ZCONTACTJID"],
        )
    )
    sender_expr = "COALESCE(" + ", ".join(sender_parts + ["''"]) + ")"

    body_parts = [
        coalesce_expr(
            "m",
            message_columns,
            ["ZTEXT", "ZBODY", "ZMESSAGE", "ZCAPTION", "ZPUSHTEXT"],
        )
    ]
    if "di" in aliases:
        body_parts.append(
            coalesce_expr(
                "di",
                data_columns,
                ["ZTEXT", "ZBODY", "ZMESSAGE", "ZCAPTION", "ZTITLE", "ZDATA"],
            )
        )
    if "mi" in aliases:
        body_parts.append(
            coalesce_expr(
                "mi",
                media_columns,
                ["ZCAPTION", "ZTITLE", "ZTEXT", "ZFILENAME"],
            )
        )
    body_expr = "COALESCE(" + ", ".join(body_parts + ["''"]) + ")"

    message_id_expr = "m.Z_PK"
    if stanza_col:
        message_id_expr = f"COALESCE({column_expr('m', stanza_col)}, m.Z_PK)"
    from_me_expr = column_expr("m", from_me_col) if from_me_col else "0"
    type_expr = column_expr("m", type_col) if type_col else "NULL"

    sql = f"""
        SELECT
          m.Z_PK AS row_pk,
          {message_id_expr} AS message_id,
          {column_expr('m', date_col)} AS raw_time,
          {sender_expr} AS sender,
          {from_me_expr} AS from_me,
          {type_expr} AS message_type,
          {body_expr} AS body
        FROM ZWAMESSAGE m
        {' '.join(joins)}
        WHERE {column_expr('m', chat_col)} = ?
          AND {column_expr('m', date_col)} >= ?
        ORDER BY {column_expr('m', date_col)} ASC, m.Z_PK ASC
    """

    try:
        rows = conn.execute(sql, (chat["chat_pk"], threshold)).fetchall()
    except sqlite3.Error as exc:
        error("SQLITE_QUERY_ERROR", str(exc))

    messages = []
    for row in rows:
        messages.append(
            {
                "message_id": normalize_text(row[1]),
                "local_time": local_time(row[2], mode, tzinfo),
                "sender": normalize_text(row[3]) or ("me" if boolish(row[4]) else ""),
                "from_me": boolish(row[4]),
                "message_type": row[5],
                "body": normalize_text(row[6]),
            }
        )

    return {
        "range": {
            "days": days,
            "start": start_local.isoformat(timespec="seconds"),
            "end": end_local.isoformat(timespec="seconds"),
            "timezone": tz_name,
        },
        "messages": messages,
    }


def main():
    args = parse_args()
    if args.days < 1:
        error("INVALID_DAYS", "--days must be at least 1")

    try:
        ZoneInfo(args.tz)
    except Exception as exc:
        error("INVALID_TIMEZONE", str(exc), tz=args.tz)

    conn = open_readonly(args.db)
    try:
        chat = resolve_group(conn, args.group)
        export = export_messages(conn, chat, args.days, args.tz)
    finally:
        conn.close()

    emit(
        {
            "status": "OK",
            "group": {
                "name": chat["name"],
                "chat_pk": chat["chat_pk"],
                "range": export["range"],
                "message_count": len(export["messages"]),
            },
            "messages": export["messages"],
        }
    )


if __name__ == "__main__":
    main()
