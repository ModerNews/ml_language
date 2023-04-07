import json
import os

import numpy as np
import requests

import matplotlib.pyplot as plt
import argparse


def setup_parser():
    argparser = argparse.ArgumentParser(
        prog='Language Detector',
        description='Detects language of given article using Pearson correlation coefficient basing of letter frequency.',
        epilog='Datasets generated using wikipedia.org articles.\nMade by Grzegorz Jagielski: https://github.com/ModerNews'
    )
    argparser.add_argument('article', type=str, help='URL of article to detect language of.')
    argparser.add_argument('-l', '--languages', type=str, nargs='+', default=('pl', 'en', 'cz'),
                           help='Languages to compare article with. Default: pl en cz')
    return argparser


def calculate_base_data_set(lang: str):
    data_set, total_chars = [0 for i in range(26)], 0
    for i in range(1000):
        article = requests.get(f"https://{lang}.wikipedia.org/wiki/Special:Random").text.lower()
        for char in range(97, 123):
            tmp = article.count(chr(char))
            data_set[char-97] += tmp
            total_chars += tmp
        print(f"Progress: {i+1}/1000")
    print("Recalculating...")
    for i in range(26):
        data_set[i] = data_set[i]/total_chars
    print(f"Checksum: {np.sum(data_set)}")
    return data_set


def calculate_control_data_set(url: str):
    data_set, total_chars = [0 for i in range(26)], 0
    article = requests.get(url).text.lower()
    for char in range(97, 123):
        tmp = article.count(chr(char))
        data_set[char-97] += tmp
        total_chars += tmp
    print("Recalculating...")
    for i in range(26):
        data_set[i] = data_set[i]/total_chars
    print(f"Checksum: {np.sum(data_set)}")
    return data_set


def compare_data_sets(base: list, control: list):
    return np.corrcoef(base, control)[0, 1]


def generate_plot(base_data_sets, control_data_set):
    plt.figure(figsize=(12, 9))
    for key in base_data_sets.keys():
        plt.scatter(list(reversed(base_data_sets[key])), range(26), label=key)
    plt.scatter(list(reversed(control_data_set)), range(26), label="control", color="red")
    plt.legend()
    plt.title("Correlation between letters and their frequency in languages")
    plt.ylabel("Letter"), plt.xlabel("Frequency")
    plt.yticks(range(26), list(reversed([chr(i) for i in range(97, 123)])))
    plt.xticks([i/100 for i in range(11)], [f"{i}%" for i in range(11)])
    plt.grid(axis='y')


def ensure_models_folder_exists():
    if not os.path.exists("models"):
        os.mkdir("models")


def load_cached_data_sets(languages=('pl', 'en', 'cz')):
    ensure_models_folder_exists()
    base_data_sets = {}
    for file in os.listdir("models"):
        if file.split(".")[1] == "json":
            if file.split(".")[0] in languages:
                base_data_sets[file.split(".")[0]] = json.loads(open(f'models/{file}', 'r').read())
    return base_data_sets


def generate_missing_base_data_sets(languages):
    ensure_models_folder_exists()
    data_sets = {}
    for lang in languages:
        print(f"Generating base data set for {lang}...")
        data_sets[lang] = calculate_base_data_set(lang)
        with open(f'models/{lang}.json', 'w') as file:
            file.write(json.dumps(data_sets[lang]))
        print(f"Generated base data set for {lang}.")
        print("All base data sets generated.")
    return data_sets


def detect_language(article: str, *, languages=('pl', 'en', 'cz'), show_plot=True):
    base_data_sets = load_cached_data_sets(languages)
    print('Base data sets loaded.')
    if missing := set(languages) - set(base_data_sets.keys()):
        print("Missing base data sets for languages: %s" % ", ".join(missing))
        generate_missing_base_data = input("Generate missing base data? (y/n): ")
        if generate_missing_base_data == "y":
            base_data_sets |= generate_missing_base_data_sets(missing)
    control_data_set = calculate_control_data_set(article)
    generate_plot(base_data_sets, control_data_set)
    return sorted(base_data_sets.keys(), key=lambda key: compare_data_sets(base_data_sets[key], control_data_set)), plt.show(dp=1200) if show_plot else None


if __name__ == "__main__":
    argparser = setup_parser()
    args = argparser.parse_args()
    print(detect_language(args.article, languages=args.languages[0].split(" ")))