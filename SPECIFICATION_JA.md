# データベース・HTTP API 仕様書

本書は **PostgreSQL のテーブル定義** と **HTTP API の仕様** のみを記載する。

---

## 1. テーブルとドメインの対応

| 概念 | テーブル | 役割 |
|------|----------|------|
| 大項目 | `public.major_categories` | 最上位の分類 |
| 中項目 | `public.middle_categories` | 大項目にぶら下がる分類 |
| ノウハウ | `public.knowhows` | 中項目に紐づく（`middle_category_id` は NULL 可）記事本文など |

---

## 2. テーブル定義

### 2.1 `public.major_categories`（大項目）

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|-----|------|------------|------|
| `id` | `integer` | NOT NULL | `nextval('major_categories_id_seq')` | 主キー |
| `name` | `varchar` | NOT NULL | — | 名称。テーブル全体でユニーク |
| `display_order` | `integer` | NOT NULL | — | 表示順 |
| `is_deleted` | `boolean` | NOT NULL | — | 論理削除フラグ |
| `created_at` | `timestamp` (tz なし) | NOT NULL | `now()` | 作成日時 |
| `updated_at` | `timestamp` (tz なし) | NOT NULL | `now()` | 更新日時 |

- **主キー**: `id`
- **ユニーク**: `name`（制約名 `major_categories_name_key`）
- **参照元**: `middle_categories.major_category_id` → `major_categories.id`

### 2.2 `public.middle_categories`（中項目）

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|-----|------|------------|------|
| `id` | `integer` | NOT NULL | `nextval('middle_categories_id_seq')` | 主キー |
| `major_category_id` | `integer` | NOT NULL | — | 親の大項目 ID（FK） |
| `name` | `varchar` | NOT NULL | — | 名称 |
| `display_order` | `integer` | NOT NULL | — | 表示順（大項目内） |
| `is_deleted` | `boolean` | NOT NULL | — | 論理削除フラグ |
| `created_at` | `timestamp` (tz なし) | NOT NULL | `now()` | 作成日時 |
| `updated_at` | `timestamp` (tz なし) | NOT NULL | `now()` | 更新日時 |

- **主キー**: `id`
- **ユニーク**: `(major_category_id, name)`（制約名 `middle_categories_major_category_id_name_key`）
- **外部キー**: `major_category_id` → `major_categories.id`
- **参照元**: `knowhows.middle_category_id` → `middle_categories.id`（DB 上で同一参照の FK が重複している場合があるが、意味は同じ）

### 2.3 `public.knowhows`（ノウハウ）

| カラム | 型 | NULL | デフォルト | 説明 |
|--------|-----|------|------------|------|
| `id` | `integer` | NOT NULL | `nextval('knowhows_id_seq')` | 主キー |
| `title` | `varchar` | NOT NULL | — | タイトル |
| `keywords` | `varchar` | NULL 可 | — | キーワード（任意） |
| `content` | `text` | NOT NULL | — | 本文 |
| `display_order` | `integer` | NOT NULL | — | 表示順 |
| `is_deleted` | `boolean` | NOT NULL | — | 論理削除フラグ |
| `created_at` | `timestamp` (tz なし) | NOT NULL | `now()` | 作成日時 |
| `updated_at` | `timestamp` (tz なし) | NOT NULL | `now()` | 更新日時 |
| `middle_category_id` | `integer` | NULL 可 | — | 中項目 ID（FK） |

- **主キー**: `id`
- **外部キー**: `middle_category_id` → `middle_categories.id`（NULL の行もスキーマ上は許容）

---

## 3. HTTP API 仕様

### 3.0 共通

- **リクエスト／レスポンス**: JSON、UTF-8。
- **日時**: レスポンスの日時は ISO 8601 形式。DB は `timestamp without time zone` のため、タイムゾーン表記は実装・シリアライズに依存する。
- **論理削除**: `is_deleted = true` の行は、一覧・詳細・名称変更の対象外。該当しない場合は `404 Not Found`（親カテゴリが無効な場合なども含む）。
- **名称の一意性**: DB のユニーク制約違反時は `409 Conflict`（レスポンス本文にエラー説明を含む実装とする）。
- **追加時の `display_order`**: 未削除行の同一スコープ内で `display_order` の最大値 + 1（大項目は全未削除大項目、中項目は同一 `major_category_id` 内の未削除中項目）。

### 3.1 大項目一覧の取得

| 項目 | 内容 |
|------|------|
| メソッド・パス | `GET /major-categories` |
| 説明 | 未削除の大項目を `display_order` 昇順、`id` 昇順で返す。 |

**レスポンス** `200 OK` — 配列。要素:

| フィールド | 型 | 説明 |
|------------|-----|------|
| `id` | integer | ID |
| `name` | string | 名称 |
| `display_order` | integer | 表示順 |
| `created_at` | string (datetime) | 作成日時 |
| `updated_at` | string (datetime) | 更新日時 |

### 3.2 大項目の追加

| 項目 | 内容 |
|------|------|
| メソッド・パス | `POST /major-categories` |

**リクエストボディ (JSON)**

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `name` | string | 必須 | 大項目名（実装では前後空白をトリムしてよい） |

**レスポンス** `201 Created` — 3.1 の要素と同形のオブジェクト。

**エラー**

| ステータス | 条件 |
|------------|------|
| `409 Conflict` | `name` のユニーク制約違反 |

### 3.3 大項目の名称変更

| 項目 | 内容 |
|------|------|
| メソッド・パス | `PATCH /major-categories/{category_id}` |
| パスパラメータ | `category_id`（integer）— 大項目 ID |

**リクエストボディ (JSON)**

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `name` | string | 必須 | 変更後の名称 |

**レスポンス** `200 OK` — 3.1 の要素と同形。

**エラー**

| ステータス | 条件 |
|------------|------|
| `404 Not Found` | ID が無い、または `is_deleted = true` |
| `409 Conflict` | 変更後 `name` が既存と重複 |

### 3.4 中項目一覧の取得（大項目 ID 指定）

| 項目 | 内容 |
|------|------|
| メソッド・パス | `GET /major-categories/{major_category_id}/middle-categories` |
| パスパラメータ | `major_category_id` — 大項目 ID |

**説明** 指定大項目が存在し未削除のとき、その下の未削除中項目を `display_order` 昇順、`id` 昇順で返す。

**レスポンス** `200 OK` — 配列。要素:

| フィールド | 型 | 説明 |
|------------|-----|------|
| `id` | integer | 中項目 ID |
| `major_category_id` | integer | 親の大項目 ID |
| `name` | string | 名称 |
| `display_order` | integer | 表示順 |
| `created_at` | string (datetime) | 作成日時 |
| `updated_at` | string (datetime) | 更新日時 |

**エラー**

| ステータス | 条件 |
|------------|------|
| `404 Not Found` | 大項目が無い、または削除済み |

### 3.5 中項目の追加（大項目 ID 指定）

| 項目 | 内容 |
|------|------|
| メソッド・パス | `POST /major-categories/{major_category_id}/middle-categories` |
| パスパラメータ | `major_category_id` |

**リクエストボディ (JSON)**

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `name` | string | 必須 | 中項目名 |

**説明** 親大項目が有効であること。新規行は `is_deleted = false`。

**レスポンス** `201 Created` — 3.4 の要素と同形。

**エラー**

| ステータス | 条件 |
|------------|------|
| `404 Not Found` | 大項目が無効 |
| `409 Conflict` | 同一 `major_category_id` 内で `name` ユニーク違反 |

### 3.6 中項目の名称変更

| 項目 | 内容 |
|------|------|
| メソッド・パス | `PATCH /middle-categories/{category_id}` |
| パスパラメータ | `category_id` — 中項目 ID |

**リクエストボディ (JSON)**

| フィールド | 型 | 必須 | 説明 |
|------------|-----|------|------|
| `name` | string | 必須 | 変更後の名称 |

**レスポンス** `200 OK` — 3.4 の要素と同形。

**エラー**

| ステータス | 条件 |
|------------|------|
| `404 Not Found` | 中項目が無い、または削除済み |
| `409 Conflict` | `(major_category_id, name)` ユニーク違反 |

### 3.7 ノウハウ一覧の取得（中項目 ID 指定）

| 項目 | 内容 |
|------|------|
| メソッド・パス | `GET /middle-categories/{middle_category_id}/knowhows` |
| パスパラメータ | `middle_category_id` |

**説明** 中項目が有効なとき、その `middle_category_id` に一致する未削除ノウハウを `display_order` 昇順、`id` 昇順で返す。**一覧レスポンスに `content`（本文）は含めない。** `middle_category_id` が NULL のノウハウは、この一覧の対象外。

**レスポンス** `200 OK` — 配列。要素:

| フィールド | 型 | 説明 |
|------------|-----|------|
| `id` | integer | ノウハウ ID |
| `title` | string | タイトル |
| `keywords` | string \| null | キーワード |
| `display_order` | integer | 表示順 |
| `middle_category_id` | integer \| null | 中項目 ID |
| `created_at` | string (datetime) | 作成日時 |
| `updated_at` | string (datetime) | 更新日時 |

**エラー**

| ステータス | 条件 |
|------------|------|
| `404 Not Found` | 中項目が無い、または削除済み |

### 3.8 ノウハウ詳細の取得

| 項目 | 内容 |
|------|------|
| メソッド・パス | `GET /knowhows/{knowhow_id}` |
| パスパラメータ | `knowhow_id` |

**説明** 未削除のノウハウ 1 件。本文 `content` を含む。

**レスポンス** `200 OK` — オブジェクト:

| フィールド | 型 | 説明 |
|------------|-----|------|
| `id` | integer | ID |
| `title` | string | タイトル |
| `keywords` | string \| null | キーワード |
| `content` | string | 本文 |
| `display_order` | integer | 表示順 |
| `middle_category_id` | integer \| null | 中項目 ID |
| `created_at` | string (datetime) | 作成日時 |
| `updated_at` | string (datetime) | 更新日時 |

**エラー**

| ステータス | 条件 |
|------------|------|
| `404 Not Found` | 無い、または削除済み |
