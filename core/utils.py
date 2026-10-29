import csv
import errno
import glob
import json
import logging
import os
import shutil
import time
from itertools import islice

import langid
from django.utils import timezone
from sentry_sdk import capture_exception

from core import config


class Utils:
    def __init__(self):
        self.environment = config.server.env

    @staticmethod
    def slugify_unicode(text, language="en"):
        if text is None or text == '':
            return text
        replacements = [[',', '-']]
        if language in ["en", "en-US", "en-GB", "english"]:
            return slugify(text, replacements=replacements)
        slug = slugify(text, replacements=replacements, allow_unicode=True)
        return slug

    @staticmethod
    def make_dir(dir_path):
        try:
            if os.path.isfile(dir_path):
                os.remove(dir_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                time.sleep(1)
            if os.path.isfile(dir_path):
                os.remove(dir_path)
                os.makedirs(dir_path)
                time.sleep(1)
        except OSError as exc:
            capture_exception(exc)
            if exc.errno != errno.EEXIST:
                raise
        except Exception as error:
            capture_exception(error)

    @staticmethod
    def delete_single_file(file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                time.sleep(1)
        except Exception as error:
            capture_exception(error)

    @staticmethod
    def remove_directory(directory_path):
        try:
            path_list = glob.glob(os.path.join(directory_path, "*"))
            for path in path_list:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    time.sleep(1)
        except Exception as error:
            capture_exception(error)

    @staticmethod
    def delete_directory(path):
        try:
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=False, onerror=None)
                time.sleep(1)
        except Exception as error:
            capture_exception(error)

    def get_logger(self, file_name):
        if os.path.exists(file_name):
            if os.path.isfile(file_name):
                os.remove(file_name)
        else:
            basename = os.path.basename(file_name)
            self.make_dir(file_name.replace(basename, ''))
        logger = logging.getLogger(file_name)
        logger.setLevel(logging.INFO)
        handler = FileHandler(os.curdir, logger, logging.FileHandler)
        logger.addHandler(handler)
        return logger

    @staticmethod
    def chunk_of_list(_list, n):
        # looping till length l
        for i in range(0, len(_list), n):
            yield _list[i:i + n]

    @staticmethod
    def get_execution_time(start_time, logger=None, prefix=None):
        end_time = timezone.datetime.now().replace(microsecond=0)
        execution_time = (end_time - start_time)
        title = f"Execution Time: {execution_time}"
        if prefix is not None:
            title = f"{prefix} {title}"
        if logger is None:
            print(title)
            return
        logger.info("Start Time: %s", str(start_time))
        logger.info("End Time: %s", str(end_time))
        logger.info(title)

    @staticmethod
    def read_line(filepath):
        if not os.path.isfile(filepath):
            return
        with open(os.path.join(filepath), 'r') as file:
            line = file.readline()
        return line

    @staticmethod
    def file_write(filepath, content):
        with open(os.path.join(filepath), 'w+') as file:
            file.write(str(content))

    @staticmethod
    def write_binary_file(filepath, content):
        with open(os.path.join(filepath), 'wb') as file:
            file.write(content)

    @staticmethod
    def read_json_file(directory, is_send_sentry=True):
        body = {}
        try:
            if os.path.exists(directory):
                with open(directory) as f:
                    body = json.load(f)
        except Exception as fnf_error:
            if is_send_sentry:
                capture_exception(fnf_error)
        return body

    @staticmethod
    def write_json_file(data, directory):
        try:
            with open(directory, "w") as outfile:
                json.dump(data, outfile, ensure_ascii=False)
                return True
        except Exception as fnf_error:
            capture_exception(fnf_error)
            return False

    @staticmethod
    def read_from_file(directory, is_send_sentry=True):
        body = {}
        try:
            if os.path.exists(directory):
                with open(directory, 'r') as file:
                    body = file.read()
        except FileNotFoundError as fnf_error:
            if is_send_sentry:
                capture_exception(fnf_error)
            else:
                print(f"read_from_file: {fnf_error}")
        return body

    @staticmethod
    def write_to_file(data, directory):
        try:
            with open(directory, "w") as out_file:
                out_file.write(data)
                return True
        except Exception as error:
            capture_exception(error)
            return False

    @staticmethod
    def append_to_file(data, directory):
        try:
            with open(directory, "a") as out_file:
                out_file.write(data)
                return True
        except Exception as error:
            capture_exception(error)
            return False

    @staticmethod
    def append_new_line(file_name, text_to_append):
        """Append given text as a new line at the end of file"""
        # Open the file in append & read mode ('a+')
        with open(file_name, "a+") as file_object:
            # Move read cursor to the start of file.
            file_object.seek(0)
            # If file is not empty then append '\n'
            data = file_object.read(100)
            if len(data) > 0:
                file_object.write("\n")
            # Append text at the end of file
            file_object.write(text_to_append)

            # Close the file
            file_object.close()

    @staticmethod
    def list_difference(li1, li2):
        return list(set(li1) - set(li2))

    @staticmethod
    def chunks_of_list(l, n):
        # For item i in a range that is a length of l,
        for i in range(0, len(l), n):
            # Create an index range for l of n items:
            yield l[i:i + n]

    @staticmethod
    def chunks_dict(data, SIZE=10000):
        it = iter(data)
        for i in range(0, len(data), SIZE):
            yield {k: data[k] for k in islice(it, SIZE)}

    @staticmethod
    def diff(li1, li2):
        return list(set(li1) - set(li2))

    @staticmethod
    def convert_to_ascii(value: str):
        return int(''.join([str(ord(c)) for c in value]))

    def get_slug(self, text, locale_code=None):
        if locale_code is None:
            detected_lang = langid.classify(text)[0]
            locale_code = str.lower(detected_lang) if detected_lang else "en"
        return self.slugify_unicode(text, locale_code)

    @staticmethod
    def dict_fetch_all(cursor):
        """Return all rows from a cursor as a dict"""
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def write_to_csv_file(data, directory, header):
        try:
            with open(directory, mode='w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(header)
                for item in data:
                    writer.writerow([item])
                return True
        except Exception as error:
            capture_exception(error)
            return False

    @staticmethod
    def append_to_csv_file(data, directory, fieldnames=None):
        try:
            with open(directory, mode='a', newline='') as csv_file:
                if fieldnames is not None:
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    if csv_file.tell() == 0:
                        writer.writeheader()
                    for row in data:
                        writer.writerow(row)
                else:
                    writer = csv.writer(csv_file)
                    for item in data:
                        writer.writerow([item])
                return True
        except Exception as error:
            capture_exception(error)
            return False

    @staticmethod
    def write_row_to_csv_file(data_dict: dict, filepath: str):
        try:
            if os.path.isfile(filepath):
                file_mode = 'a'
            else:
                file_mode = 'w'
            with open(filepath, file_mode, encoding='utf-8') as file:
                fieldnames = list(data_dict.keys())
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if file_mode == 'w':
                    writer.writeheader()
                writer.writerow(data_dict)
            return True
        except Exception as error:
            capture_exception(error)
            return False


class FileHandler(object):

    def __init__(self, dir, logger, handler_factory, **kw):
        kw['filename'] = os.path.join(dir, logger.name)
        self._handler = handler_factory(**kw)

    def __getattr__(self, n):
        if hasattr(self._handler, n):
            return getattr(self._handler, n)
        raise AttributeError(n)
