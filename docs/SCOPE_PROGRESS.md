# 練習お客様AI 開発進捗状況

## Phase進捗

このプロジェクトはAIコントローラー型（LINEチャットボット）のため、Phase 3/4/8はスキップします。

- [x] Phase 1: 要件定義（Agent 1）
- [x] Phase 2: Git管理（Agent 2）
- Phase 3: フロントエンド基盤 — スキップ（UIなし）
- Phase 4: ページ実装 — スキップ（UIなし）
- [x] Phase 5: 環境構築（Agent 5）— pyproject.toml / .env.local テンプレート作成
- [x] Phase 6: バックエンド計画（Agent 6）— ディレクトリ構造・モジュール責務確定
- [x] Phase 7: バックエンド実装（Agent 7）— Webhook + Claude連携 + Quick Reply
- Phase 8: API統合 — スキップ（フロントエンドなし）
- [ ] Phase 9: E2Eテスト（Agent 9）— LINEシミュレータでの統合テスト
- [ ] Phase 10: ローカル動作確認（Agent 10）— ngrok経由で実機LINEから動作確認
- [ ] Phase 11: デプロイ（Agent 11）— Renderへデプロイ

## エンドポイント管理表

| ID | エンドポイント | メソッド | 機能 | 着手 | 完了 |
|----|--------------|---------|------|------|------|
| E-001 | /webhook/line | POST | LINE Webhook受信→処理→返信（Follow含む） | [x] | [x] |
| E-002 | /api/health | GET | ヘルスチェック | [x] | [x] |

## 内部ツール（関数）管理表

| ID | 関数名 | 役割 | 着手 | 完了 |
|----|-------|------|------|------|
| T-001 | WebhookParser.parse | LINE署名検証（SDK標準） | [x] | [x] |
| T-002 | detect_trigger | トリガーワード検出 | [x] | [x] |
| T-003 | get_session | セッション取得or作成 | [x] | [x] |
| T-004 | call_patient_ai | 患者役Claude呼び出し | [x] | [x] |
| T-005 | call_scoring_ai | 採点役Claude呼び出し | [x] | [x] |
| T-006 | _reply (line_handler) | LINE返信 | [x] | [x] |
| T-007 | reset_session | セッション初期化 | [x] | [x] |
| T-008 | cleanup_expired_sessions | TTL超過セッション削除 | [x] | [x] |

## システムプロンプト管理表

| ID | 名称 | 用途 | 着手 | 完了 |
|----|------|------|------|------|
| P-001 | 患者役（田中美咲） | 練習中の患者ロールプレイ | [x] | [x] |
| P-002 | 採点役 | 5項目×10点採点 | [x] | [x] |

## 外部アカウント準備状況

| サービス | アカウント | APIキー/トークン | セットアップ |
|---------|-----------|----------------|------------|
| LINE Developers | [ ] | [ ] Channel Secret / Access Token | [ ] チャネル作成・Webhook URL設定 |
| Anthropic API | [ ] | [ ] ANTHROPIC_API_KEY | [ ] 課金設定 |
| Render | [ ] | — | [ ] サービス作成・環境変数設定 |
