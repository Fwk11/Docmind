# 这是 Prompt 管理模块，保存各类分析任务的模板。

SUMMARY_PROMPT = "请阅读以下内容并给出简洁的摘要：\n\n{context}\n\n摘要："
KEYWORDS_PROMPT = "请从以下内容中提取关键词，返回关键词列表：\n\n{context}\n\n关键词："
KNOWLEDGE_POINTS_PROMPT = "请从以下内容中提取知识点，并按照要点形式输出：\n\n{context}\n\n知识点："
CHAPTER_SUMMARY_PROMPT = "请基于以下章节内容生成章节总结：\n\n{context}\n\n章节总结："
