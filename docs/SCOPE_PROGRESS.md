# 練習お客様AI 開発進捗状況

## Phase進捗

このプロジェクトはAIコントローラー型（LINEチャットボット）のため、Phase 3/4/8はスキップします。

- [x] Phase 1: 要件定義（Agent 1）
- [x] Phase 2: Git管理（Agent 2）
- Phase 3: フロントエンド基盤 — スキップ（UIなし）
- Phase 4: ページ実装 — スキップ（UIなし）
- [ ] Phase 5: 環境構築（Agent 5）— LINE Developers / Anthropic APIキー設定
- [ ] Phase 6: バックエンド計画（Agent 6）— FastAPI実装計画策定
- [ ] Phase 7: バックエンド実装（Agent 7）— Webhook + Claude連携
- Phase 8: API統合 — スキップ（フロントエンドなし）
- [ ] Phase 9: E2Eテスト（Agent 9）— LINEシミュレータでの統合テスト
- [ ] Phase 10: ローカル動作確認（Agent 10）— ngrok経由で実機LINEから動作確認
- [ ] Phase 11: デプロイ（Agent 11）— Renderへデプロイ

## エンドポイント管理表

| ID | エンドポイント | メソッド | 機能 | 着手 | 完了 |
|----|--------------|---------|------|------|------|
| E-001 | /webhook/line | POST | LINE Webhook受信→処理→返信 | [ ] | [ ] |
| E-002 | /api/health | GET | ヘルスチェック | [ ] | [ ] |

## 内部ツール（関数）管理表

| ID | 関数名 | 役割 | 着手 | 完了 |
|----|-------|------|------|------|
| T-001 | verify_line_signature | LINE署名検証 | [ ] | [ ] |
| T-002 | detect_trigger | トリガーワード検出 | [ ] | [ ] |
| T-003 | get_session | セッション取得or作成 | [ ] | [ ] |
| T-004 | call_patient_ai | 患者役Claude呼び出し | [ ] | [ ] |
| T-005 | call_scoring_ai | 採点役Claude呼び出し | [ ] | [ ] |
| T-006 | reply_to_line | LINE返信 | [ ] | [ ] |
| T-007 | reset_session | セッション初期化 | [ ] | [ ] |
| T-008 | cleanup_expired_sessions | TTL超過セッション削除 | [ ] | [ ] |

## システムプロンプト管理表

| ID | 名称 | 用途 | 着手 | 完了 |
|----|------|------|------|------|
| P-001 | 患者役（田中美咲） | 練習中の患者ロールプレイ | [ ] | [ ] |
| P-002 | 採点役 | 5項目×10点採点 | [ ] | [ ] |

## 外部アカウント準備状況

| サービス | アカウント | APIキー/トークン | セットアップ |
|---------|-----------|----------------|------------|
| LINE Developers | [ ] | [ ] Channel Secret / Access Token | [ ] チャネル作成・Webhook URL設定 |
| Anthropic API | [ ] | [ ] ANTHROPIC_API_KEY | [ ] 課金設定 |
| Render | [ ] | — | [ ] サービス作成・環境変数設定 |
