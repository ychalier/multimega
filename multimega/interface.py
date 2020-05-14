"""
Extend mega.py default class for improved upload progress
"""
import os
import random
import logging
import requests
from Crypto.Cipher import AES
from Crypto.Util import Counter
import tqdm  # pylint: disable=E0401
import mega  # pylint: disable=E0401
from mega.crypto import (  # pylint: disable=E0401
    a32_to_base64, encrypt_key, base64_url_encode, encrypt_attr,
    a32_to_str, get_chunks, str_to_a32,
    makebyte,
)


class MegaInterface(mega.Mega):  # pylint: disable=R0903
    """
    Extend mega.py default class for improved upload progress. Everyting here
    is copy/pasted from the .upload() method of the mega.Mega class, except
    what is related to tqdm progress bar.
    """

    def progress_upload(self, filename, dest=None, dest_filename=None):  # pylint: disable=R0914,R0915
        """
        Custom upload method with nicer progress
        """
        logger = logging.getLogger(__name__)
        # determine storage node
        if dest is None:
            # if none set, upload to cloud drive node
            if not hasattr(self, 'root_id'):
                self.get_files()
            dest = self.root_id

        # request upload url, call 'u' method
        with open(filename, 'rb') as input_file:
            file_size = os.path.getsize(filename)
            ul_url = self._api_request({'a': 'u', 's': file_size})['p']

            # generate random aes key (128) for file
            ul_key = [random.randint(0, 0xFFFFFFFF) for _ in range(6)]
            k_str = a32_to_str(ul_key[:4])
            count = Counter.new(
                128, initial_value=((ul_key[4] << 32) + ul_key[5]) << 64
            )
            aes = AES.new(k_str, AES.MODE_CTR, counter=count)

            upload_progress = 0
            completion_file_handle = None

            mac_str = '\0' * 16
            mac_encryptor = AES.new(
                k_str, AES.MODE_CBC, mac_str.encode("utf8")
            )
            iv_str = a32_to_str([ul_key[4], ul_key[5], ul_key[4], ul_key[5]])
            if file_size > 0:
                pbar = tqdm.tqdm(total=file_size, unit="b", unit_scale=True, unit_divisor=1024)
                for chunk_start, chunk_size in get_chunks(file_size):
                    chunk = input_file.read(chunk_size)
                    upload_progress += len(chunk)

                    encryptor = AES.new(k_str, AES.MODE_CBC, iv_str)
                    for i in range(0, len(chunk) - 16, 16):
                        block = chunk[i:i + 16]
                        encryptor.encrypt(block)

                    # fix for files under 16 bytes failing
                    if file_size > 16:
                        i += 16
                    else:
                        i = 0

                    block = chunk[i:i + 16]
                    if len(block) % 16:
                        block += makebyte('\0' * (16 - len(block) % 16))
                    mac_str = mac_encryptor.encrypt(encryptor.encrypt(block))

                    # encrypt file and upload
                    chunk = aes.encrypt(chunk)
                    output_file = requests.post(
                        ul_url + "/" + str(chunk_start),
                        data=chunk,
                        timeout=self.timeout
                    )
                    completion_file_handle = output_file.text
                    pbar.update(len(chunk))
                pbar.close()
            else:
                output_file = requests.post(
                    ul_url + "/0", data='', timeout=self.timeout
                )
                completion_file_handle = output_file.text

            logger.info('Chunks uploaded')
            logger.info('Setting attributes to complete upload')
            logger.info('Computing attributes')
            file_mac = str_to_a32(mac_str)

            # determine meta mac
            meta_mac = (file_mac[0] ^ file_mac[1], file_mac[2] ^ file_mac[3])

            dest_filename = dest_filename or os.path.basename(filename)
            attribs = {'n': dest_filename}

            encrypt_attribs = base64_url_encode(
                encrypt_attr(attribs, ul_key[:4])
            )
            key = [
                ul_key[0] ^ ul_key[4], ul_key[1] ^ ul_key[5],
                ul_key[2] ^ meta_mac[0], ul_key[3] ^ meta_mac[1], ul_key[4],
                ul_key[5], meta_mac[0], meta_mac[1]
            ]
            encrypted_key = a32_to_base64(encrypt_key(key, self.master_key))
            logger.info('Sending request to update attributes')
            # update attributes
            data = self._api_request(
                {
                    'a': 'p',
                    't': dest,
                    'i': self.request_id,
                    'n': [
                        {
                            'h': completion_file_handle,
                            't': 0,
                            'a': encrypt_attribs,
                            'k': encrypted_key
                        }
                    ]
                }
            )
            logger.info('Upload complete')
            return data
