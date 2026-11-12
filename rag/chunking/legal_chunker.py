
import re

from config.config import (
    CHUNK_MAX_TOKENS,
    OVERLAP_TOKENS
)


class LegalChunker:

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.max_tokens = CHUNK_MAX_TOKENS
        self.overlap_tokens = OVERLAP_TOKENS

    def chunk_document(self, document_id, document):
        document_title = document.get("title", "")

        chunks = []
        articles = self._find_articles(document)

        for article in articles:
            article_chunks = self._chunk_article(
                article=article,
                document_id=document_id,
                document_title=document_title
            )

            chunks.extend(article_chunks)

        for index, chunk in enumerate(chunks):
            chunk["chunk_index"] = index

        return chunks

    def _find_articles(self, node):
        articles = []

        if node.get("type") == "ARTICLE":
            articles.append(node)
            return articles

        for child in node.get("children", []):
            articles.extend(self._find_articles(child))

        return articles

    def _chunk_article(self, article, document_id, document_title):
        article_number = article.get("number")
        content = article.get("content", "").strip()

        if not content:
            return []

        prefix = f"{document_title} | Члан {article_number}\n\n"

        full_text = prefix + content

        total_tokens = self._count_tokens(full_text)

        parent_id = f"{document_id}:article:{article_number}"

        # Ako član staje u jedan chunk, ne delimo ga.
        if total_tokens <= self.max_tokens:
            return [
                self._create_chunk(
                    document_id,
                    article_number,
                    content,
                    prefix,
                    parent_id,
                    chunk_type="ARTICLE",
                    chunk_part=0,
                    total_chunks=1
                )
            ]

        # Član prelazi limit: delimo ga na pasuse.
        print(f"Article number {article_number} is too long. Splitting into paragraphs...")
        paragraphs = self._split_into_paragraphs(content)

        number_of_chunks = (
            total_tokens + self.max_tokens - 1
        ) // self.max_tokens

        chunks_content = self._distribute_paragraphs(
            paragraphs=paragraphs,
            prefix=prefix,
            number_of_chunks=number_of_chunks
        )

        total_chunks = len(chunks_content)

        return [
            self._create_chunk(
                document_id,
                article_number,
                chunk_content,
                prefix,
                parent_id,
                chunk_type="PARAGRAPH",
                chunk_part=index,
                total_chunks=total_chunks
            )
            for index, chunk_content in enumerate(chunks_content)
        ]

    def _split_into_paragraphs(self, content):
        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", content)
            if paragraph.strip()
        ]

        if len(paragraphs) <= 1:
            paragraphs = [
                paragraph.strip()
                for paragraph in re.split(r"\n+", content)
                if paragraph.strip()
            ]

        return paragraphs

    def _distribute_paragraphs(
        self,
        paragraphs,
        prefix,
        number_of_chunks
    ):
        chunks = []
        current_paragraphs = []

        target_tokens = self.max_tokens

        for paragraph in paragraphs:
            candidate = "\n\n".join(
                current_paragraphs + [paragraph]
            )

            candidate_tokens = self._count_tokens(
                prefix + candidate
            )

            if candidate_tokens <= target_tokens:
                current_paragraphs.append(paragraph)
                continue

            if current_paragraphs:
                chunks.append("\n\n".join(current_paragraphs))

                current_paragraphs = self._get_overlap_paragraphs(
                    current_paragraphs
                )

            if self._count_tokens(prefix + paragraph) > self.max_tokens:
                sentence_parts = self._split_large_paragraph(
                    paragraph,
                    prefix
                )

                for part in sentence_parts:
                    candidate = "\n\n".join(
                        current_paragraphs + [part]
                    )

                    if self._count_tokens(prefix + candidate) <= self.max_tokens:
                        current_paragraphs.append(part)
                    else:
                        if current_paragraphs:
                            chunks.append(
                                "\n\n".join(current_paragraphs)
                            )

                        current_paragraphs = [part]

            else:
                current_paragraphs.append(paragraph)

        if current_paragraphs:
            chunks.append("\n\n".join(current_paragraphs))

        return chunks

    def _get_overlap_paragraphs(self, paragraphs):
        overlap = []
        overlap_tokens = 0

        for paragraph in reversed(paragraphs):
            paragraph_tokens = self._count_tokens(paragraph)

            if overlap_tokens + paragraph_tokens > self.overlap_tokens:
                break

            overlap.insert(0, paragraph)
            overlap_tokens += paragraph_tokens

        return overlap

    def _split_large_paragraph(self, paragraph, prefix):
        sentences = [
            sentence.strip()
            for sentence in re.split(
                r"(?<=[.!?])\s+",
                paragraph
            )
            if sentence.strip()
        ]

        if len(sentences) <= 1:
            return self._split_by_words(paragraph, prefix)

        parts = []
        current_sentences = []

        for sentence in sentences:
            candidate = " ".join(
                current_sentences + [sentence]
            )

            if self._count_tokens(prefix + candidate) <= self.max_tokens:
                current_sentences.append(sentence)
                continue

            if current_sentences:
                parts.append(" ".join(current_sentences))

            current_sentences = [sentence]

        if current_sentences:
            parts.append(" ".join(current_sentences))

        return parts

    def _split_by_words(self, text, prefix):
        words = text.split()

        parts = []
        current_words = []

        for word in words:
            candidate = " ".join(current_words + [word])

            if self._count_tokens(prefix + candidate) <= self.max_tokens:
                current_words.append(word)
            else:
                if current_words:
                    parts.append(" ".join(current_words))

                current_words = [word]

        if current_words:
            parts.append(" ".join(current_words))

        return parts

    def _create_chunk(
        self,
        document_id,
        article_number,
        content,
        prefix,
        parent_id,
        chunk_type,
        chunk_part,
        total_chunks
    ):
        return {
            "document_id": document_id,
            "article_number": article_number,
            "chunk_type": chunk_type,
            "content": content,
            "embedding_text": prefix + content,
            "metadata": {
                "parent_id": parent_id,
                "chunk_part": chunk_part,
                "total_chunks": total_chunks
            }
        }

    def _count_tokens(self, text):
        return self.tokenizer.count_tokens(text)
