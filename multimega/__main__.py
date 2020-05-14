"""
Interface for a multiaccount MEGA cloud service
"""

import argparse
import logging
from multimega import Operator


def main():
    """
    Argument parsing and action execution
    """
    log_format = "%(asctime)s\t%(levelname)s\t%(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database", type=str, help="")
    subparsers = parser.add_subparsers(dest="object", required=True)
    account_parser = subparsers.add_parser("account")
    account_subparsers = account_parser.add_subparsers(dest="action", required=True)
    account_subparsers.add_parser("create")
    account_subparsers.add_parser("list")
    account_sync_parser = account_subparsers.add_parser("sync")
    account_sync_parser.add_argument("login", type=str, help="account login")
    file_parser = subparsers.add_parser("file")
    file_subparsers = file_parser.add_subparsers(dest="action", required=True)
    file_upload_parser = file_subparsers.add_parser("upload")
    file_upload_parser.add_argument(
        "path",
        type=str,
        help="path to the file or directory to upload"
    )
    file_upload_parser.add_argument(
        "name",
        type=str,
        help="name of the uploaded file"
    )
    file_upload_parser.add_argument(
        "-p", "--password",
        type=str,
        help="encryption password"
    )
    file_list_parser = file_subparsers.add_parser("list")
    file_list_parser.add_argument(
        "-f",
        "--format",
        choices=["txt", "json", "csv", "html"],
        default="txt",
        help="list output format"
    )
    file_delete_parser = file_subparsers.add_parser("delete")
    file_delete_parser.add_argument(
        "name",
        type=str,
        help="filename to delete"
    )
    file_find_parser = file_subparsers.add_parser("find")
    file_find_parser.add_argument(
        "name",
        type=str,
        help="filename to find"
    )
    args = parser.parse_args()
    operator = Operator("db.sqlite3")
    if args.object == "account":
        if args.action == "create":
            operator.create_account()
        elif args.action == "list":
            operator.list_accounts()
        elif args.action == "sync":
            operator.sync_account(args.login)
    elif args.object == "file":
        if args.action == "upload":
            operator.upload_file(args.path, args.name, args.password)
        elif args.action == "list":
            operator.list_files(args.format)
        elif args.action == "delete":
            operator.delete_file(args.name)
        elif args.action == "find":
            operator.find_file(args.name)

main()
