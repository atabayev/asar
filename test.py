import os, os.path


def count_files(dir):
    return len([name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))])

    # path joining version for other paths


if __name__ == '__main__':
    count_files('')
