import glob
import json
import os.path

# TODO use median value instead
MIN_SCORE = 512


def parse_post(post):
    # if post.get('removed_by') is not None:
    #     print("following post was removed: ", post)
    #     continue

    if '[deleted]' in post.get('selftext'):
        # print("post content was deleted: ", post['title'], post['selftext'])
        # print(str(post), '\n')
        return None

    if '[removed]' in post.get('selftext'):
        return None

    return {
        'score': post['score'],
        'title': post['title'],
        'selftext': post['selftext'],

        'upvote_ratio': post.get('upvote_ratio', -1),
        'author': post['author'],
        'permalink': post['permalink'],
        # 'created_utc': post['created_utc'],
        'utc_datetime_str': post['utc_datetime_str']
    }


def to_skip(post):
    return post['score'] < MIN_SCORE


def parse_folder(path: str):
    result = []

    grand_total = 0
    grand_archived = 0
    grand_skipped = 0

    for file in glob.glob(path):
        with open(file, 'r') as f:
            content = f.read()
            posts = json.loads(content)['data']

            total = 0
            archived = 0

            for post in posts:
                total += 1

                parsed_post = parse_post(post)

                if parsed_post is None:
                    archived += 1
                    continue

                if to_skip(post):
                    grand_skipped += 1
                    continue

                result.append(parsed_post)

        grand_total += total
        grand_archived += archived
        # print("total: ", total, ", archived: ", archived)

    result.sort(key=lambda k: k.get('score'), reverse=True)
    print(
        f"result size: {len(result)}, grand archived: {grand_archived}, grand skipped: {grand_skipped}, grand total: {grand_total}")

    return result


def write_result_to_json_file(posts: list, filename: str):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)


def write_result_to_plain_file(posts: list, filename: str):
    with open(filename, 'w', encoding='utf-8') as f:
        for post in posts:
            title = post['title']
            body = post['selftext']

            f.write(title)
            if not title.endswith('.'):
                f.write(". ")
            f.write(body)
            f.write('\n')


def get_datasets_list(root: str) -> list[str]:
    return [d for d in glob.glob(root) if os.path.isdir(d)]


datasets = get_datasets_list("./datasets/*")
for dataset_dir in datasets:
    print(f"parsing {dataset_dir}")

    posts = parse_folder(f'{dataset_dir}/*')
    write_result_to_json_file(posts, f"./{dataset_dir}.json")
    write_result_to_plain_file(posts, f"./{dataset_dir}.txt")

