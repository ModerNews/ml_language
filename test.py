import main


def test(languages):
    for lang in languages:
        counter = 0
        languages_counter = {lang: 0 for lang in languages}
        print('Currently testing language: %s' % lang)
        for i in range(500):
            tmp = main.detect_language(f"https://{lang}.wikipedia.org/wiki/Special:Random", languages=languages, show_plot=False)[0][0]
            counter += 1 if lang == tmp else 0
            languages_counter[tmp] += 1
            print(f"Progress: {i+1}/500")
        print("=====================================")
        print(f"Language: {lang}:")
        print(f"Accuracy: {counter/500} ({counter}/500)")
        print(f"Most commonly guessed: {max(languages_counter, key=languages_counter.get)} ({languages_counter[max(languages_counter, key=languages_counter.get)]}/500)")
        print("=====================================")

languages = ('pl', 'en', 'cz')
print('Testing with custom set of languages: %s' % str(languages))
test(languages)

