from sklearn.metrics.pairwise import paired_cosine_distances


"""
Get the cosine similiarities between each pair of sentences in a dataset.

Parameters:
    dataset : IdiomDataset (src/data/idiom_dataset.py)
        A dataset containing all the sentences to compare.
    model : SentenceTransformer
        The model to evaluate sentences.

Returns:
    cosine_scores : TODO
        All of the cosine similarities for the sentence pairs.
"""
def get_dataset_similarities(dataset, model):
    return get_similarities(dataset.sentence1s, dataset.sentence2s, model, show_progress_bar=True)


"""
Get the cosine similiarities between each pair of sentences in a dataset.

Parameters:
    sentence1s : list[str]
        A list of sentences to compare.
    sentence2s : list[str]
        A list of sentences to compare.
    model : SentenceTransformer
        The model to evaluate sentences.
    show_progress_bar : bool
        Whether to show the progress bar for evaluation, useful for large amounts of data. Default is False.

Returns:
    cosine_scores : TODO
        All of the cosine similarities for the sentence pairs.
"""
def get_similarities(sentence1s, sentence2s, model, show_progress_bar=False):

    #Compute embedding for both lists
    embeddings1 = model.encode(sentence1s, show_progress_bar=show_progress_bar, convert_to_numpy=True)
    embeddings2 = model.encode(sentence2s, show_progress_bar=show_progress_bar, convert_to_numpy=True)

    # Compute cosine-similarits
    cosine_scores = 1 - (paired_cosine_distances(embeddings1, embeddings2))

    return cosine_scores

