# RAG評価テンプレートの設計思想（ハッカソン提出用）

## 本テンプレートの主張
- RAG/Agentの本質は「検索精度」だけでなく「評価・運用設計」にある
- 何を“良し”とし、何を“失敗”とみなすかの思想が重要
- コードは最低限のmust_include判定・hallucination判定のみ公開
- 本番用の詳細ロジック・閾値設計・改善判断は非公開

## 評価設計のポイント
- 設問ごとに qid, type, must_include, ideal_answer を定義
- answer() を呼び出し、生成回答をmust_includeで判定
- hallucination（出典不明回答）も単純なルールで判定
- failure_tagsや改善判断は思想のみ記載、ロジックは非公開

## 例：must_include判定
- 生成回答が must_include の全語を含むかどうか
- 例: `def check_must_include(generated, must_include): return all(k in generated for k in must_include)`

## 例：hallucination判定
- 出典情報が空なら hallucination=True
- 例: `hallucination = (len(sources) == 0)`

## 本番用ロジックとの違い
- 類似度閾値・recall/noise_rate・failure_tags付与・改善判断は非公開
- 詳細な評価基準はprivate版で管理

## まとめ
- 「思想＋最低限の動く評価コード」を重視
- 本番用の知見・ノウハウは資産として非公開
