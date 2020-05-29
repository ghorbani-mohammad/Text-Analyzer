def category(spacy_model, np, punctuation, news_id, categories):
    doc = spacy_model(news_id.body.lower().replace('\n',''))
    doc = [word for word in doc if not word.is_stop and str(word) not in punctuation]

    categories_label = list(categories.values_list('army_category_id', flat=True).distinct())
    temp_score = []
    similarity = {}
    total = 0
    for cat_id in categories_label:
        keywords = list(categories.filter(army_category_id=cat_id).values_list('army_keyword_id__label', flat=True).distinct())
        for keyword in keywords:
            token = spacy_model(keyword)
            if token.has_vector:
                for word in doc:
                    if word.has_vector:
                        sim = word.similarity(token)
                        if sim > 0.59:
                            temp_score.append(sim)
                    else:
                        pass
        if temp_score:
            similarity[cat_id] = (np.mean(temp_score) * len(temp_score)) / len(keywords)
            total += similarity[cat_id]
            temp_score = []
        else:
            similarity[cat_id] = 0
    
    for key in similarity:
        if total == similarity[key]:
            similarity[key] = round(similarity[key] * 100)
        else:
            similarity[key] = round(similarity[key] / total * 100)

    return similarity