import subprocess
import os
from glob import glob
import ntpath
import re
import itertools

__author__ = 'Charles'


def main():
    repo_url = "https://bitbucket.org/cgathuru/dnsclient.git"
    dir_name = ntpath.basename(repo_url)[:-4]
    print(dir_name)
    git_commit_fields = ['id', 'author_name', 'author_email', 'date', 'message', 'other']
    git_log_format = ['%H', '%an', '%ae', '%ad', '%s']
    if not os.path.exists(dir_name):
        clone_repo(repo_url)
    # home = os.path.expanduser("~")
    # os.chdir(home)
    # os.chdir("Desktop")
    os.chdir(dir_name)
    print(os.getcwd())
    with open("test.txt", mode='r') as f:
        logs = f.read()

        logs = logs.strip().split("\n")
        f.close()
    #  future(git_commit_fields, git_log_format)
    print('list of size ' + str(len(logs)))

    parse_framework_functions(logs, [])


def parse_framework_functions(lines: list, frameworks: list) -> list:
    if frameworks is None:
        frameworks = []
    added_content = []
    removed_content = []
    change_diff = {}
    is_new_func = False
    is_func_content = False
    bracket_cnt = 0
    start_line = 0
    start_line_rev = 0
    start_ln_cnt = [False, "", False, ""]
    change_lines = (0, 0, 0, 0)
    func_spacing = 4
    class_name = ''
    first_seen = False
    first_seen_rev = False
    removed_ln_num = [0]*2
    added_ln_num = [0]*2
    args = {}
    for line in lines:

        # Get the class name
        if line.startswith("---"):
            m = re.search("/([A-za-z0-9]+).java", line)
            if m:
                class_name = m.group(1)
        if line.startswith("+++"):
            m = re.search("/([A-za-z0-9]+).java", line)
            if m:
                new_class_name = m.group(1)
                if new_class_name is not class_name:
                    change_diff['class_rename'] = (True, class_name, new_class_name)
                    class_name = new_class_name
                else:
                    change_diff['class_rename'] = (False, class_name)

        # Get the changed lines
        if line.startswith("@@"):
            # There may be content so we need to add it before proceeding
            add_content_and_clear(frameworks, added_content, removed_content)
            print(line)
            m = re.search('@@\s-(\d+),(\d+)\s\+(\d+),(\d+)', line)
            if m:
                start_line = start_line_rev = int(m.group(1))
                change_lines = tuple(map(int, m.groups()))
                args['change_lines'] = change_lines
                start_ln_cnt = [True, line]*2  # Notify that we need to start counting

        # First thing we need to do is determine where the lines changes are i.e. what lines
        # have been removed and what lines have been added. We will use two counters
        # TODO Determine line numbers that are changes
        if line.startswith("+ "):
            # TODO something
            start_line += 1

            if not first_seen:
                added_ln_num = [start_line]*2
            else:
                added_ln_num[1] = start_line  # Increment for global change

            # Now we need to get the changed content.
            added_content.append(line)

        elif line.startswith("- "):
            # TODO something
            start_line_rev += 1

            if not first_seen_rev:
                removed_ln_num = [start_line_rev]*2
            else:
                removed_ln_num[1] = start_line_rev  # Increment for global change

            # Now we need to get the removed content
            removed_content.append(line)
        else:

            if start_ln_cnt[0] and start_ln_cnt[1] != line:
                start_line += 1
            if start_ln_cnt[2] and start_ln_cnt[3] != line:
                start_line_rev += 1

        # Now we need to look for the end of a patch. This can be identified by the start of a new one
        if line.startswith("diff --git"):
            print("Reached end of patch diff")
            add_content_and_clear(frameworks, added_content, removed_content)

    print("Printing frameworks")
    print("There are " + str(len(frameworks)))
    # for framework in frameworks:
        # print(framework.get_name())
        #print(framework.get_content())


def add_content_and_clear(frameworks, added_content, removed_content, **kwargs):
    filter_content_and_add(frameworks, list(removed_content), **kwargs)
    filter_content_and_add(frameworks, list(added_content), **kwargs)
    # TODO Clear all temp variables
    added_content.clear()
    removed_content.clear()


def filter_content_and_add(frameworks, contents, **kwargs):
    # TODO filter the content
    # First we need to determine if the content is valid
    added_ln_num = kwargs.get('added_ln_num', [0]*2)
    removed_ln_num = kwargs.get('removed_ln_num', [0]*2)

    is_add = kwargs.get('add', True)

    intersection = [val for val in list(range(removed_ln_num[0], removed_ln_num[1]+1)) if val in
                    list(range(added_ln_num[0], added_ln_num[1]+1))]

    # There are 3 cases we need to determine
    # 1. Removal
    # 2. Replacement
    # 3. Addition
    if is_add:

        if intersection:
            results = is_content_in_framework(frameworks, intersection)
            if results:
                # We need to do a replacement
                for result in results:
                    lif, framework = result
                    # lif is a tuple of start index and end index
                    framework.replace_content_from(
                        list(contents[(lif[0] - added_ln_num[0]): (lif[1]+1 - added_ln_num[0])]), lif[0])
                kwargs = dict(kwargs)
                added_ln_num[0] += len(lif)
                kwargs.update({"added_ln_num": added_ln_num})
                # filter_content_and_add(frameworks, contents[lif[1]+1 -:], **kwargs)
            else:
                # Intersection must have been comments
                pass
        # TODO filter content to add
        # First we determine if the content is a framework function
        # We do this by parsing of checking if its existing
        lif, framework = is_content_in_framework(frameworks, added_ln_num)
        pass
    else:
        # We must be removing

        # We need to make sure that replacement are only performed on adds
        if intersection:
            return

        # TODO filter content to remove

    add_content_to_framework(frameworks, contents, **kwargs)
    return


def is_content_in_framework(frameworks, line_nums) -> list:
    result = []
    for framework in frameworks:
        intersections = framework.contains_lines(line_nums)
        intersections = list(ranges(intersections))
        if not intersections:
            for intersection in intersections:
                result.append((intersection, framework))
    return result


def ranges(i):
    def function(p):
        x, y = p
        return y - x

    for a, b in itertools.groupby(enumerate(i), function):
        b = list(b)
        yield b[0][1], b[-1][1]


def add_content_to_framework(frameworks: list, content: list, **kwargs):
    # TODO figure out what to add/remove
    # We first need to unpack arguments
    # self.num_holes = kwargs.get('num_holes',random_holes())
    is_add = kwargs.get('add', True)

    # Next we need to figure out if we are adding or removing

    return


def is_modification(line_no: int, change_list: tuple) -> bool:
    return line_no < (change_list[2]+change_list[0])


# Can't test this out as git is not in my path
def future(git_commit_fields, git_log_format):
    p = subprocess.Popen('git log --format="%s"' % git_log_format, shell=True, stdout=subprocess.PIPE,
                         universal_newlines=True)
    (log, _) = p.communicate()
    log = log.strip('\n\x1e').split("\x1e")
    print("Printing log...")
    for row in log:
        print(row)
    log = [dict(zip(git_commit_fields, row)) for row in log]
    # java_files = [y for x in os.walk(dir_name) for y in glob(os.path.join(x[0], '*.java'))]
    print("Printing separated data")
    print(log)


def clone_repo(repo_url: str) -> list:
    subprocess.call(["git clone", repo_url])


class FrameworkFunction:

    def __init__(self, name: str, content: list, class_name: str, start_line: int=0, end_line: int=0,
                 num_revisions: int=0):
        self.start_line = start_line
        self.end_line = end_line
        self.name = name
        self.content = content
        self.num_revisions = num_revisions
        self.class_name = class_name

    def __len__(self):
        return len(self.content)

    def get_size(self) -> int:
        return len(self.content)

    def get_start_line(self) -> int:
        return self.start_line

    def set_start_line(self, start_line: int):
        self.start_line = start_line

    def get_end_line(self) -> int:
        return self.get_end_line()

    def set_end_line(self, end_line: int):
        self.end_line = end_line

    def get_content(self) -> list:
        return self.content

    def set_content(self, content: list):
        self.content = content
        self.start_line = content[0]
        self.update_end_line()

    def append_content_end(self, content: list):
        self.content += content
        self.update_end_line()

    def replace_content_from(self, content: list, start_index: int):
        if start_index <= len(self.content) - 1:
            self.content = self.content[:start_index] + content
        else:
            self.append_content_end(content)

        self.update_end_line()

    def insert_content_from(self, content: list, start_index: int):
        if start_index <= len(self.content) - 1:
            self.content = self.content[:start_index] + content + self.content[start_index:]
        else:
            self.append_content_end(content)

        self.update_end_line()

    def update_end_line(self):
        self.end_line = self.start_line + len(self)  # Update end index

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str):
        self.name = name

    def get_num_revisions(self) -> int:
        return self.num_revisions

    def set_num_revisions(self, num_revisions: int):
        self.num_revisions = num_revisions

    def contains_change(self, line_num: int) -> bool:
        return (self.end_line >= line_num) and (self.start_line <= line_num)

    def contains_lines(self, lines: list) -> list:
        return [val for val in lines if val in list(range(self.start_line, self.end_line+1))]

if __name__ == '__main__':
    main()


