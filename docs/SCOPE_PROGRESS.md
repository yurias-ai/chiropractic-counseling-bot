# 練習お客様AI 開発進捗状況

## Phase進捗

このプロジェクトは「URLを開くだけで体験できるデモ」のため、一部のPhaseは簡略化しています。

- [x] Phase 1: 要件定義（Agent 1）
- [x] Phase 2: Git管理（Agent 2）
- [x] Phase 3: フロントエンド基盤 — 静的HTML + Vanilla JS（ビルド不要、`static/index.html`）
- [x] Phase 4: ページ実装 — チャットUI（バブル/タイピング/採点カード）
- [x] Phase 5: 環境構築（Agent 5）— pyproject.toml / .env.local テンプレート作成
- [x] Phase 6: バックエンド計画（Agent 6）— ディレクトリ構造・モジュール責務確定
- [x] Phase 7: バックエンド実装（Agent 7）— FastAPI + Claude連携 + /api/practice/*
- [x] Phase 8: API統合 — フロントとバックを同一オリジンで配信
- [x] Phase 9: E2Eテスト（Agent 9）— ブラウザ実機テスト（表情切替・音声・採点）
- [x] Phase 10: ローカル動作確認（Agent 10）— `localhost:8940` で1セッション完走
- [x] Phase 11: デプロイ（Agent 11）— Render 無料プランに公開（Basic認証付き）

## 公開URL
https://chiro-counseling-bot.onrender.com

ログイン情報は Render ダッシュボード → chiro-counseling-bot → Environment の `BASIC_AUTH_USERS` を参照。
ローカルでは `.env.local` の `BASIC_AUTH_USERS` に同じ値が設定されている。

## 追加機能（デモ向け強化）
- 田中美咲さんの5表情写真自動切替（neutral / nervous / worried / relieved / thinking）
- 音声入力（Web Speech API、Chrome/Safari対応）
- 患者の音声読み上げ（Web Speech Synthesis、ON/OFF切替可）
- HTTP Basic認証で2ユーザー限定アクセス

## エンドポイント管理表

| ID | エンドポイント | メソッド | 機能 | 着手 | 完了 |
|----|--------------|---------|------|------|------|
| E-000 | / | GET | チャットUI（index.html）配信 | [x] | [x] |
| E-001 | /api/practice/start | POST | 練習開始（患者初回挨拶生成） | [x] | [x] |
| E-002 | /api/practice/message | POST | ユーザー発言→患者応答 | [x] | [x] |
| E-003 | /api/practice/score | POST | 採点生成（終了後セッションリセット） | [x] | [x] |
| E-004 | /api/practice/reset | POST | セッションリセット | [x] | [x] |
| E-005 | /api/health | GET | ヘルスチェック | [x] | [x] |

## 内部ツール（関数）管理表

| ID | 関数名 | 役割 | 着手 | 完了 |
|----|-------|------|------|------|
| T-001 | get_session | セッション取得or作成 | [x] | [x] |
| T-002 | start_practice | 患者役の初回挨拶を生成 | [x] | [x] |
| T-003 | continue_practice | 会話継続（履歴追加→応答生成） | [x] | [x] |
| T-004 | call_patient_ai | 患者役Claude呼び出し | [x] | [x] |
| T-005 | call_scoring_ai | 採点役Claude呼び出し | [x] | [x] |
| T-006 | reset_session | セッション初期化 | [x] | [x] |
| T-007 | cleanup_expired_sessions | TTL超過セッション削除 | [x] | [x] |

## システムプロンプト管理表

| ID | 名称 | 用途 | 着手 | 完了 |
|----|------|------|------|------|
| P-001 | 患者役（田中美咲） | 練習中の患者ロールプレイ | [x] | [x] |
| P-002 | 採点役 | 5項目×10点採点 | [x] | [x] |

## 外部アカウント準備状況

| サービス | アカウント | APIキー/トークン | セットアップ |
|---------|-----------|----------------|------------|
| Anthropic API | [x] | [x] ANTHROPIC_API_KEY | [x] 課金設定 |
| Render | [x] | — | [x] サービス作成・環境変数設定 |
