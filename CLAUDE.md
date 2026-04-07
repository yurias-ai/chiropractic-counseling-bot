# 練習お客様AI

## 基本原則
> 「シンプルさは究極の洗練である」

- **最小性**: 不要なコードは一文字も残さない。必要最小限を超えない
- **単一性**: 真実の源は常に一つ（要件: docs/requirements.md、進捗: docs/SCOPE_PROGRESS.md）
- **刹那性**: 役目を終えたコード・ドキュメントは即座に削除する
- **実証性**: 推測しない。ログ・APIレスポンスで事実を確認する
- **潔癖性**: エラーは隠さない。フォールバックで問題を隠蔽しない

## プロジェクト概要

カイロプラクター見習い向けの初回カウンセリング練習LINEボット。
患者役AIとの対話練習＋5項目採点フィードバックで、問診力を鍛える。

## アプローチ
**AIコントローラー型（チャットボット）** — UIなし、LINEのトーク画面が唯一のインターフェース

## 技術スタック

```yaml
言語: Python 3.11+
フレームワーク: FastAPI + uvicorn
LINE SDK: line-bot-sdk-python (v3)
AI SDK: anthropic
モデル: claude-sonnet-4-5
パッケージ管理: uv
セッション管理: インメモリdict + TTL（デモ）
デプロイ: Render
```

## ポート設定

```yaml
backend: 8940
```

※ ローカル開発時は ngrok でこのポートを公開してLINE Webhook URLに設定する。

## 環境変数

`.env.local` に配置（プロジェクトルート）:

```
LINE_CHANNEL_SECRET=...
LINE_CHANNEL_ACCESS_TOKEN=...
ANTHROPIC_API_KEY=...
PORT=8940
SESSION_TTL_SECONDS=3600
```

### 共通ルール
- 設定モジュール: `src/config/__init__.py`（os.environ集約）
- ハードコード禁止: `os.environ` はconfig経由のみ
- **絶対禁止**: `.env`, `.env.test`, `.env.development`, `.env.example` は作成しない

## 命名規則

- ファイル/モジュール: snake_case.py
- クラス: PascalCase
- 関数・変数: snake_case
- 定数: UPPER_SNAKE_CASE

## ディレクトリ構成（予定）

```
src/
├── main.py              # FastAPIエントリーポイント
├── config/__init__.py   # 環境変数集約
├── webhook/
│   └── line_handler.py  # /webhook/line ハンドラー
├── ai/
│   ├── patient.py       # 患者役Claude呼び出し
│   ├── scoring.py       # 採点役Claude呼び出し
│   └── prompts.py       # システムプロンプト定義
├── session/
│   └── store.py         # インメモリセッションストア + TTL
└── utils/
    └── line_signature.py # 署名検証
```

## コード品質

- 関数: 100行以下 / ファイル: 700行以下 / 複雑度: 10以下 / 行長: 120文字

## 開発ルール

### サーバー起動
- `uv run uvicorn src.main:app --reload --port 8940`
- 既存プロセスを確認してから起動（`lsof -i :8940`）
- サーバーは1つのみ維持

### LINE Webhook開発
- ローカル開発時は `ngrok http 8940` で公開
- 取得したHTTPS URL + `/webhook/line` を LINE Developers の Webhook URL に設定
- 「Webhookの利用」を ON、「応答メッセージ」を OFF にする

### エラー対応
- 環境変数エラー → 全タスク停止、即報告（試行錯誤禁止）
- LINE署名検証失敗 → 401返却、ログ記録
- Claude APIエラー → ユーザーに「混雑しています」返信、ログ記録
- 同じエラー3回 → Web検索で最新情報を収集

### デプロイ
- デプロイはユーザーの明示的な承認を得てから実行
- Renderへ環境変数を設定してから push

### ドキュメント管理
許可されたドキュメントのみ:
- `docs/requirements.md`（要件定義）
- `docs/SCOPE_PROGRESS.md`（進捗管理）
- `docs/DEPLOYMENT.md`（デプロイ情報、後続Phaseで作成）
上記以外はユーザー許諾が必要。

## AIエージェント設計

このプロジェクトは**シンプルプロンプト型**:
- Claude APIを1回呼び出すのみ（Tool Use不要、自律ループ不要）
- 患者役: system + 会話履歴 → 1回応答
- 採点役: system + 会話履歴テキスト化 → 1回応答
- ストリーミング不要（LINEは一括返信）

## 将来拡張

- v1.1: 患者プリセット4種選択
- v1.2: カスタム患者入力
- v1.3: 総合指導法（サプリ・寝具・体操・スキンケア）提案練習モード
- v2.0: Supabase導入で履歴永続化

## CI/CD設定

### GitHub Actions（PR時に自動実行）
| チェック | 対象 | コマンド |
|---------|------|---------|
| TypeScript | frontend | `npx tsc --noEmit` |
| Lint (JS/TS) | frontend | `npm run lint` |
| Build | frontend | `npm run build` |
| Lint (Python) | backend | `flake8 --max-line-length=120` |
| Format (Python) | backend | `black --check --line-length=120` |

### ブランチ戦略
- `main`: 本番環境
- `develop`: 開発統合ブランチ
- `feature/*`: 機能開発ブランチ

### リポジトリ
- URL: https://github.com/yurias-ai/chiropractic-counseling-bot
- 公開設定: Public
