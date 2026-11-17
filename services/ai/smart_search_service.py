import os
import json
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import Config
from dao.experience_dao import ExperienceDAO
from dao.ai_dao import AIDaO

logger = logging.getLogger(__name__)

class SmartSearchService:
    _model = None
    _faiss_index = None
    _experience_ids = []
    _metadata = {}

    @classmethod
    def _get_embedding_model(cls):
        """Lazy load sentence-transformers model."""
        if cls._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                cls._model = SentenceTransformer(Config.EMBEDDING_MODEL_NAME)
                logger.info(f"Loaded SentenceTransformer: {Config.EMBEDDING_MODEL_NAME}")
            except Exception as e:
                logger.error(f"Failed to load SentenceTransformer: {e}. Semantic search will use keyword/TF-IDF similarity fallback.")
                cls._model = False
        return cls._model

    @classmethod
    def build_experience_corpus_text(cls, exp) -> str:
        """Create privacy-safe searchable text without personal user info."""
        parts = [
            f"Company: {exp.company_name}",
            f"Role: {exp.job_role}",
            f"Difficulty: {exp.difficulty}",
            f"Level: {exp.experience_level}",
            f"Rounds: {exp.interview_rounds}",
            f"Technical Questions: {exp.technical_questions or ''}",
            f"HR Questions: {exp.hr_questions or ''}",
            f"Experience Summary: {exp.overall_experience or ''}",
            f"Preparation Advice: {exp.preparation_tips or ''}"
        ]
        return "\n".join(parts)

    @classmethod
    def index_approved_experiences(cls):
        """Build or refresh vector index from all approved experiences."""
        approved_exps = ExperienceDAO.get_approved(limit=1000)
        if not approved_exps:
            logger.info("No approved experiences to index.")
            return

        texts = [cls.build_experience_corpus_text(e) for e in approved_exps]
        ids = [e.id for e in approved_exps]

        model = cls._get_embedding_model()
        if model:
            try:
                import faiss
                embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                dim = embeddings.shape[1]
                index = faiss.IndexFlatIP(dim) # Inner product with normalized vectors = Cosine similarity
                index.add(embeddings.astype(np.float32))
                cls._faiss_index = index
                cls._experience_ids = ids
                logger.info(f"Indexed {len(ids)} experiences into FAISS.")
                return
            except Exception as e:
                logger.error(f"FAISS indexing error: {e}")

        # Store for fallback cosine similarity
        cls._experience_ids = ids

    @classmethod
    def search(cls, query: str, company: Optional[str] = None,
               role: Optional[str] = None, difficulty: Optional[str] = None,
               level: Optional[str] = None, top_k: int = 10,
               user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Execute semantic search with relational filters and snippet explanation.
        """
        if not query or not query.strip():
            # Return regular filtered approved experiences
            exps = ExperienceDAO.get_approved(
                company=company, role=role, difficulty=difficulty,
                experience_level=level, limit=top_k
            )
            return [{'experience': e, 'similarity_score': 1.0, 'match_snippet': 'Matched standard filters'} for e in exps]

        # Log search query
        clean_query = query.strip()
        
        # Load all candidate approved experiences matching hard filters first
        candidate_exps = ExperienceDAO.get_approved(
            company=company, role=role, difficulty=difficulty,
            experience_level=level, limit=200
        )
        if not candidate_exps:
            AIDaO.log_search(user_id, clean_query, 0)
            return []

        model = cls._get_embedding_model()
        results = []

        if model:
            try:
                query_vector = model.encode([clean_query], convert_to_numpy=True, normalize_embeddings=True)[0]
                doc_texts = [cls.build_experience_corpus_text(e) for e in candidate_exps]
                doc_vectors = model.encode(doc_texts, convert_to_numpy=True, normalize_embeddings=True)

                # Compute cosine similarities
                similarities = np.dot(doc_vectors, query_vector)

                for idx, score in enumerate(similarities):
                    exp = candidate_exps[idx]
                    snippet = cls._extract_matching_snippet(clean_query, exp)
                    results.append({
                        'experience': exp,
                        'similarity_score': round(float(score) * 100, 1),
                        'match_snippet': snippet
                    })

                # Sort by similarity descending
                results.sort(key=lambda x: x['similarity_score'], reverse=True)
            except Exception as e:
                logger.error(f"Vector search failed: {e}. Using token overlap fallback.")
                results = cls._keyword_overlap_search(clean_query, candidate_exps)
        else:
            results = cls._keyword_overlap_search(clean_query, candidate_exps)

        final_results = results[:top_k]
        AIDaO.log_search(user_id, clean_query, len(final_results))
        return final_results

    @classmethod
    def _keyword_overlap_search(cls, query: str, experiences: List[Any]) -> List[Dict[str, Any]]:
        """Fallback token-matching search when embeddings are not available."""
        query_words = set(query.lower().split())
        scored = []
        for exp in experiences:
            text = cls.build_experience_corpus_text(exp).lower()
            overlap = sum(1 for w in query_words if w in text)
            score = (overlap / max(len(query_words), 1)) * 100
            snippet = cls._extract_matching_snippet(query, exp)
            scored.append({
                'experience': exp,
                'similarity_score': round(score, 1),
                'match_snippet': snippet
            })
        scored.sort(key=lambda x: x['similarity_score'], reverse=True)
        return scored

    @classmethod
    def _extract_matching_snippet(cls, query: str, exp) -> str:
        """Find the most relevant sentence or question segment explaining why it matched."""
        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        corpus = cls.build_experience_corpus_text(exp)
        sentences = corpus.split("\n")
        
        best_sentence = ""
        best_matches = 0
        for s in sentences:
            matches = sum(1 for term in query_terms if term in s.lower())
            if matches > best_matches:
                best_matches = matches
                best_sentence = s.strip()

        if best_sentence:
            return best_sentence[:220]
        return f"Matched role: {exp.job_role} at {exp.company_name} ({exp.difficulty} difficulty)"
