import json
import re
import zipfile
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_corpus(corpus_file="dataset.json"):
    documents = []
    try:
        with open(corpus_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    doc = json.loads(line)
                except json.JSONDecodeError:
                    continue
                text = f"{doc.get('title', '')} {doc.get('content', '')}"
                documents.append(text)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {corpus_file}.")
    return documents

def make_submission(test_file="/kaggle/input/datasets/phnguynvnb22dckh087/ktrattt/de_thi.json", corpus_file="/kaggle/input/datasets/phnguynvnb22dckh087/ktrattt/dataset.json", output_file="/kaggle/working/submission.json"):
    documents = load_corpus(corpus_file)
    if not documents:
        return

    # Thay đổi 1: TfidfVectorizer thêm ngram_range=(1,2), sublinear_tf=True, max_df=0.95
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        max_df=0.95
    )
    doc_vectors = vectorizer.fit_transform(documents)
    
    # Tạo danh sách từ vựng cho từng document để tính overlap sau này
    doc_words_list = []
    for doc in documents:
        words = set(re.findall(r'\w+', doc.lower()))
        doc_words_list.append(words)

    with open(test_file, 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    
    submissions = []
    valid_choices = ["A", "B", "C", "D"]
    
    for item in test_data:
        question_id = item.get("id")
        question_text = item.get("question", "")
        
        # Thay đổi 2: Retrieval top_k=35
        query_vector = vectorizer.transform([question_text])
        similarities = cosine_similarity(query_vector, doc_vectors).flatten()
        # Lấy chỉ số top 35 và sắp xếp giảm dần
        top_k_indices = np.argsort(similarities)[-35:][::-1]
        
        best_choice = "A"
        max_choice_score = -1.0
        
        # Thay đổi 3: Scoring với hypothesis riêng cho mỗi choice
        for choice_key in valid_choices:
            choice_text = item.get(choice_key, "")
            if not choice_text:
                continue
                
            choice_words = set(re.findall(r'\w+', choice_text.lower()))
            if not choice_words:
                continue
            
            hypothesis_text = f"{question_text} {choice_text}"
            hypothesis_vector = vectorizer.transform([hypothesis_text])
            
            # Tính điểm cho từng doc trong top_k
            local_scores = []
            for idx in top_k_indices:
                doc_vec = doc_vectors[idx]
                doc_words = doc_words_list[idx]
                
                # Cosine similarity
                cos_sim = cosine_similarity(hypothesis_vector, doc_vec)[0][0]
                
                # Overlap score: len(choice_words & doc_words) / len(choice_words)
                overlap_count = len(choice_words & doc_words)
                overlap_score = overlap_count / len(choice_words)
                
                # Tổng hợp: cos * 0.8 + overlap * 0.2
                final_score = cos_sim * 0.8 + overlap_score * 0.2
                local_scores.append(final_score)
            
            # Lấy max score RIÊNG cho choice này trong top_k docs
            if local_scores:
                choice_max_score = max(local_scores)
                
                if choice_max_score > max_choice_score:
                    max_choice_score = choice_max_score
                    best_choice = choice_key
        
        submissions.append({"id": question_id, "answer": best_choice})

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(submissions, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    make_submission()
