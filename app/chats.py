import os
import json
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "users.db")


def _conn():
    return sqlite3.connect(DB_PATH)


def get_user_id(username: str) -> int | None:
    conn = _conn()
    try:
        row = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def build_context(df, file_name: str) -> str:
    """Construye un contexto compacto en JSON a partir de un DataFrame."""
    context = {
        "file": file_name,
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "columns": {col: str(df[col].dtype) for col in df.columns},
        "stats": json.loads(df.describe(include="all").fillna("").to_json()),
        "sample": json.loads(df.head(5).to_json(orient="records", date_format="iso")),
    }
    return json.dumps(context, ensure_ascii=False, separators=(",", ":"))


def context_to_prompt(context_str: str) -> str:
    """Expande el contexto compacto a texto legible para la IA."""
    if not context_str:
        return ""
    try:
        ctx = json.loads(context_str)
        cols = ", ".join(f"{k} ({v})" for k, v in ctx.get("columns", {}).items())
        sample_str = json.dumps(ctx.get("sample", []), ensure_ascii=False, indent=2)
        stats_str = json.dumps(ctx.get("stats", {}), ensure_ascii=False, indent=2)
        return (
            f"Archivo: {ctx.get('file', '?')}\n"
            f"Dimensiones: {ctx.get('rows', '?')} filas x {ctx.get('cols', '?')} columnas\n"
            f"Columnas: {cols}\n\n"
            f"Estadísticas:\n{stats_str}\n\n"
            f"Muestra (5 filas):\n{sample_str}"
        )
    except Exception:
        return context_str


def crear_chat(user_id: int, name: str = "Nuevo chat") -> int | None:
    conn = _conn()
    try:
        cursor = conn.execute(
            "INSERT INTO chats (user_id, name) VALUES (?, ?)",
            (user_id, name),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def obtener_chats(user_id: int) -> list[dict]:
    conn = _conn()
    try:
        rows = conn.execute(
            "SELECT id, name, file_name, updated_at FROM chats WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,),
        ).fetchall()
        return [{"id": r[0], "name": r[1], "file_name": r[2], "updated_at": r[3]} for r in rows]
    finally:
        conn.close()


def obtener_chat(chat_id: int) -> dict | None:
    conn = _conn()
    try:
        row = conn.execute(
            "SELECT id, user_id, name, file_name, data_context FROM chats WHERE id = ?",
            (chat_id,),
        ).fetchone()
        if row:
            return {"id": row[0], "user_id": row[1], "name": row[2], "file_name": row[3], "data_context": row[4]}
        return None
    finally:
        conn.close()


def actualizar_chat(chat_id: int, name: str = None, data_context: str = None, file_name: str = None) -> bool:
    fields, values = [], []
    if name is not None:
        fields.append("name = ?")
        values.append(name)
    if data_context is not None:
        fields.append("data_context = ?")
        values.append(data_context)
    if file_name is not None:
        fields.append("file_name = ?")
        values.append(file_name)
    if not fields:
        return False
    fields.append("updated_at = CURRENT_TIMESTAMP")
    values.append(chat_id)
    conn = _conn()
    try:
        conn.execute(f"UPDATE chats SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()


def eliminar_chat(chat_id: int) -> bool:
    conn = _conn()
    try:
        conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()


def guardar_mensaje(chat_id: int, role: str, content: str) -> bool:
    conn = _conn()
    try:
        conn.execute(
            "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
            (chat_id, role, content),
        )
        conn.execute("UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (chat_id,))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()


def obtener_mensajes(chat_id: int) -> list[dict]:
    conn = _conn()
    try:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY created_at ASC",
            (chat_id,),
        ).fetchall()
        return [{"role": r[0], "content": r[1]} for r in rows]
    finally:
        conn.close()
