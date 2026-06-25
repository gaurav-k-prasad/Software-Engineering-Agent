import argparse
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class IntentSpec:
    queries: list[str]
    expected: list[str]


ROOT = Path(__file__).resolve().parents[1]
CHUNK_INDEX_PATH = ROOT / "output.jsonl"
DEFAULT_OUTPUT_PATH = ROOT / "rag_eval_dataset_symbolic.jsonl"


def load_target_index(path: Path) -> set[str]:
    targets: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = json.loads(line)
            targets.add(record.get("qualified_name", ""))
            targets.add(record.get("module_path", ""))
            targets.add(record.get("file_path", ""))
    return {target for target in targets if target}


def build_natural_language_specs() -> list[IntentSpec]:
    return [
        IntentSpec(
            queries=[
                "Show me where the user login happens",
                "Where is the login flow implemented for users?",
                "Find the code path that authenticates a user during login",
                "What handles user sign in in this app?",
                "Which function runs when a user logs in?",
            ],
            expected=[
                "module.UserControllersClass.login_user",
                "module.log_in",
                "module.LoginUser",
                "module.PasswordManager.verify_password",
                "module.JWTManager.create_access_token",
                "module.JWTManager.create_refresh_token",
            ],
        ),
        IntentSpec(
            queries=[
                "Show me where user registration is handled",
                "Where does signup create a new user account?",
                "Find the code for the user signup flow",
                "What happens when someone signs up?",
                "Which function creates a new user record?",
            ],
            expected=[
                "module.UserControllersClass.signup_user",
                "module.sign_up",
                "module.SignUpUser",
                "module.UserControllersClass._validate_signup_input",
                "module.PasswordManager.encode_and_hash_password",
                "module.EmailServices.send_account_verification_email",
            ],
        ),
        IntentSpec(
            queries=[
                "Where is account verification handled after signup?",
                "Show me the email verification flow",
                "Find the code that verifies a new user account",
                "Which function confirms a user's email address?",
                "Where is the verification token checked?",
            ],
            expected=[
                "module.UserControllersClass.user_account_verification_controller",
                "module.user_account_verification",
                "module.EmailServices.send_account_verification_confirmation_email",
                "module.JWTManager.decode_jwt_token_without_expirytime",
            ],
        ),
        IntentSpec(
            queries=[
                "Where is the forgot password email sent?",
                "Show me the password reset link flow",
                "Find the code that sends a reset password email",
                "Which function handles forgot password?",
                "Where do users request a password reset email?",
            ],
            expected=[
                "module.UserControllersClass.send_password_reset_email_controller",
                "module.send_password_reset_email",
                "module.EmailServices.send_password_reset_email",
            ],
        ),
        IntentSpec(
            queries=[
                "Where does the password reset happen after clicking the link?",
                "Show me the final reset password flow",
                "Find the code that updates a password from reset token",
                "Which function completes a password reset?",
                "Where is the reset password form handled?",
            ],
            expected=[
                "module.UserControllersClass.password_reset_controller",
                "module.reset_password",
                "module.EmailServices.send_password_reset_confirmation_email",
            ],
        ),
        IntentSpec(
            queries=[
                "Where is token refresh handled?",
                "Show me the refresh token flow",
                "Find the code that issues new access tokens",
                "Which endpoint refreshes a session?",
                "Where does the app renew an expired token?",
            ],
            expected=[
                "module.UserControllersClass.refresh_token_controller",
                "module.refresh_token",
                "module.token_required",
                "module.TokenValidator",
                "module.JWTManager.create_access_token",
                "module.JWTManager.create_refresh_token",
            ],
        ),
        IntentSpec(
            queries=[
                "Where is logout handled?",
                "Show me the user logout code",
                "Find the endpoint that signs a user out",
                "Which function removes the user's session?",
                "Where does logout delete tokens?",
            ],
            expected=[
                "module.UserControllersClass.logout_user",
                "module.logout",
                "module.JWTManager.decode_jwt_token_without_expirytime",
                "module.TokenValidator",
            ],
        ),
        IntentSpec(
            queries=[
                "Where is token validation implemented?",
                "Show me the dependency that checks access tokens",
                "Find the class that validates bearer tokens",
                "Which code verifies sessions before protected routes?",
                "Where is the auth dependency for refresh and access tokens?",
            ],
            expected=[
                "backend.src.dependencies.user_auth_dependency",
                "module.TokenValidator",
                "module.TokenValidator._validate_token",
                "module.token_required",
                "module.JWTManager.decode_token",
                "module.MongoDBConnection.start_connection",
                "module.MongoDBConnection.get_collection",
                "module.MongoDBConnection.close_connection",
            ],
        ),
        IntentSpec(
            queries=[
                "Where is JWT encoding and decoding implemented?",
                "Show me the JWT manager code",
                "Find the access and refresh token logic",
                "Which class creates and decodes JWTs?",
                "Where are token expiry rules defined?",
            ],
            expected=[
                "backend.src.config.jwt_token",
                "module.JWTManager",
                "module.JWTManager.create_access_token",
                "module.JWTManager.create_refresh_token",
                "module.JWTManager.decode_token",
                "module.JWTManager.decode_jwt_token_without_expirytime",
            ],
        ),
        IntentSpec(
            queries=[
                "Where is password hashing handled?",
                "Show me the password manager code",
                "Find the function that hashes passwords with bcrypt",
                "Which method checks password strength?",
                "Where do we verify stored passwords?",
            ],
            expected=[
                "backend.src.config.security",
                "module.PasswordManager",
                "module.PasswordManager.encode_and_hash_password",
                "module.PasswordManager.verify_password",
                "module.PasswordManager.is_password_strong_enough",
            ],
        ),
        IntentSpec(
            queries=[
                "Where is the MongoDB connection wrapper?",
                "Show me the database connection code",
                "Find the class that opens and closes MongoDB",
                "Which module returns collections from MongoDB?",
                "Where is the app's database connection managed?",
            ],
            expected=[
                "backend.src.config.database",
                "module.MongoDBConnection",
                "module.MongoDBConnection.__init__",
                "module.MongoDBConnection.start_connection",
                "module.MongoDBConnection.get_collection",
                "module.MongoDBConnection.close_connection",
            ],
        ),
        IntentSpec(
            queries=[
                "Where are email notification workflows implemented?",
                "Show me the email service class",
                "Find the code that sends verification and reset emails",
                "Which functions send account emails?",
                "Where is the mail service for users?",
            ],
            expected=[
                "backend.src.services.email_services",
                "module.EmailServices",
                "module.EmailServices.send_account_verification_email",
                "module.EmailServices.send_account_verification_confirmation_email",
                "module.EmailServices.send_password_reset_email",
                "module.EmailServices.send_password_reset_confirmation_email",
            ],
        ),
        IntentSpec(
            queries=[
                "Where are the user schemas defined?",
                "Show me the pydantic models for users",
                "Find the request and response models for auth",
                "Which schema names describe signup and login payloads?",
                "Where are user session models stored?",
            ],
            expected=[
                "backend.src.schemas.user_schema",
                "module.SignUpUser",
                "module.LoginUser",
                "module.RefreshTokenStore",
                "module.UserSessionStore",
                "module.User",
                "module.individual_user_data",
                "module.all_user_data",
            ],
        ),
        IntentSpec(
            queries=[
                "Where is the book creation flow?",
                "Show me how a book gets added",
                "Find the code that inserts a new book",
                "Which endpoint creates a book record?",
                "Where is add book implemented?",
            ],
            expected=[
                "module.BookController.add_book",
                "module.add_book",
                "module.AddBookRequest",
                "module.Book",
                "module.book_data",
                "module.generate_unique_key",
            ],
        ),
        IntentSpec(
            queries=[
                "Where is the list all books flow?",
                "Show me the code that fetches all books",
                "Find the endpoint for getting a user's books",
                "Which function returns all books for a user?",
                "Where is the all books query implemented?",
            ],
            expected=[
                "module.BookController.get_all_books",
                "module.get_all_books",
                "module.all_books_data",
                "module.book_data",
            ],
        ),
        IntentSpec(
            queries=[
                "Where is the book lookup by id flow?",
                "Show me how a single book is fetched",
                "Find the code that reads one book by book id",
                "Which endpoint gets a book detail page?",
                "Where is get book by id implemented?",
            ],
            expected=[
                "module.BookController.get_book_by_id",
                "module.get_book_by_id",
                "module.book_data",
            ],
        ),
        IntentSpec(
            queries=[
                "Where is book update handled?",
                "Show me the update book flow",
                "Find the code that edits book details",
                "Which endpoint updates a book record?",
                "Where is update book implemented?",
            ],
            expected=[
                "module.BookController.update_book",
                "module.update_book",
                "module.UpdateBookRequest",
            ],
        ),
        IntentSpec(
            queries=[
                "Where is book deletion handled?",
                "Show me the delete book flow",
                "Find the code that removes a book",
                "Which endpoint deletes a book record?",
                "Where is delete book implemented?",
            ],
            expected=[
                "module.BookController.delete_book",
                "module.delete_book",
            ],
        ),
        IntentSpec(
            queries=[
                "Where are the book schemas defined?",
                "Show me the pydantic models for books",
                "Find the request and response models for book CRUD",
                "Which book model names should I index?",
                "Where is the book schema file?",
            ],
            expected=[
                "backend.src.schemas.book_schema",
                "module.AddBookRequest",
                "module.Book",
                "module.UpdateBookRequest",
            ],
        ),
        IntentSpec(
            queries=[
                "Where is the app entry point wired together?",
                "Show me the FastAPI startup module",
                "Find the file that includes the routers",
                "Which code creates the FastAPI app?",
                "Where is the main server bootstrap?",
            ],
            expected=[
                "backend.main",
                "module.root",
                "backend.src.routes.user_route",
                "backend.src.routes.book_route",
            ],
        ),
    ]


def build_symbolic_specs() -> list[IntentSpec]:
    return [
        IntentSpec(
            queries=[
                "login_user",
                "log_in",
                "verify_password",
                "create_access_token",
                "create_refresh_token",
            ],
            expected=[
                "module.UserControllersClass.login_user",
                "module.log_in",
                "module.LoginUser",
                "module.PasswordManager.verify_password",
                "module.JWTManager.create_access_token",
                "module.JWTManager.create_refresh_token",
            ],
        ),
        IntentSpec(
            queries=[
                "signup_user",
                "sign_up",
                "validate_signup_input",
                "encode_and_hash_password",
                "send_account_verification_email",
            ],
            expected=[
                "module.UserControllersClass.signup_user",
                "module.sign_up",
                "module.SignUpUser",
                "module.UserControllersClass._validate_signup_input",
                "module.PasswordManager.encode_and_hash_password",
                "module.EmailServices.send_account_verification_email",
            ],
        ),
        IntentSpec(
            queries=[
                "user_account_verification_controller",
                "user_account_verification",
                "send_account_verification_confirmation_email",
                "decode_jwt_token_without_expirytime",
                "verify_email_token",
            ],
            expected=[
                "module.UserControllersClass.user_account_verification_controller",
                "module.user_account_verification",
                "module.EmailServices.send_account_verification_confirmation_email",
                "module.JWTManager.decode_jwt_token_without_expirytime",
            ],
        ),
        IntentSpec(
            queries=[
                "send_password_reset_email_controller",
                "send_password_reset_email",
                "password_reset_email",
                "password_reset_link",
                "password_reset_request",
            ],
            expected=[
                "module.UserControllersClass.send_password_reset_email_controller",
                "module.send_password_reset_email",
                "module.EmailServices.send_password_reset_email",
            ],
        ),
        IntentSpec(
            queries=[
                "password_reset_controller",
                "reset_password",
                "password_reset_confirmation_email",
                "reset_token",
                "reset_password_form",
            ],
            expected=[
                "module.UserControllersClass.password_reset_controller",
                "module.reset_password",
                "module.EmailServices.send_password_reset_confirmation_email",
            ],
        ),
        IntentSpec(
            queries=[
                "refresh_token_controller",
                "refresh_token",
                "token_required",
                "TokenValidator",
                "issue_access_token",
            ],
            expected=[
                "module.UserControllersClass.refresh_token_controller",
                "module.refresh_token",
                "module.token_required",
                "module.TokenValidator",
                "module.JWTManager.create_access_token",
                "module.JWTManager.create_refresh_token",
            ],
        ),
        IntentSpec(
            queries=[
                "logout_user",
                "logout",
                "decode_jwt_token_without_expirytime",
                "TokenValidator",
                "clear_session",
            ],
            expected=[
                "module.UserControllersClass.logout_user",
                "module.logout",
                "module.JWTManager.decode_jwt_token_without_expirytime",
                "module.TokenValidator",
            ],
        ),
        IntentSpec(
            queries=[
                "user_auth_dependency",
                "TokenValidator",
                "validate_token",
                "decode_token",
                "mongo_collection",
            ],
            expected=[
                "backend.src.dependencies.user_auth_dependency",
                "module.TokenValidator",
                "module.TokenValidator._validate_token",
                "module.token_required",
                "module.JWTManager.decode_token",
                "module.MongoDBConnection.start_connection",
                "module.MongoDBConnection.get_collection",
                "module.MongoDBConnection.close_connection",
            ],
        ),
        IntentSpec(
            queries=[
                "jwt_token",
                "JWTManager",
                "create_access_token",
                "create_refresh_token",
                "decode_token",
            ],
            expected=[
                "backend.src.config.jwt_token",
                "module.JWTManager",
                "module.JWTManager.create_access_token",
                "module.JWTManager.create_refresh_token",
                "module.JWTManager.decode_token",
                "module.JWTManager.decode_jwt_token_without_expirytime",
            ],
        ),
        IntentSpec(
            queries=[
                "security",
                "PasswordManager",
                "encode_and_hash_password",
                "verify_password",
                "is_password_strong_enough",
            ],
            expected=[
                "backend.src.config.security",
                "module.PasswordManager",
                "module.PasswordManager.encode_and_hash_password",
                "module.PasswordManager.verify_password",
                "module.PasswordManager.is_password_strong_enough",
            ],
        ),
        IntentSpec(
            queries=[
                "database",
                "MongoDBConnection",
                "start_connection",
                "get_collection",
                "close_connection",
            ],
            expected=[
                "backend.src.config.database",
                "module.MongoDBConnection",
                "module.MongoDBConnection.__init__",
                "module.MongoDBConnection.start_connection",
                "module.MongoDBConnection.get_collection",
                "module.MongoDBConnection.close_connection",
            ],
        ),
        IntentSpec(
            queries=[
                "email_services",
                "EmailServices",
                "send_account_verification_email",
                "send_account_verification_confirmation_email",
                "send_password_reset_email",
            ],
            expected=[
                "backend.src.services.email_services",
                "module.EmailServices",
                "module.EmailServices.send_account_verification_email",
                "module.EmailServices.send_account_verification_confirmation_email",
                "module.EmailServices.send_password_reset_email",
                "module.EmailServices.send_password_reset_confirmation_email",
            ],
        ),
        IntentSpec(
            queries=[
                "user_schema",
                "SignUpUser",
                "LoginUser",
                "RefreshTokenStore",
                "UserSessionStore",
            ],
            expected=[
                "backend.src.schemas.user_schema",
                "module.SignUpUser",
                "module.LoginUser",
                "module.RefreshTokenStore",
                "module.UserSessionStore",
                "module.User",
                "module.individual_user_data",
                "module.all_user_data",
            ],
        ),
        IntentSpec(
            queries=[
                "add_book",
                "book_data",
                "generate_unique_key",
                "BookController",
                "AddBookRequest",
            ],
            expected=[
                "module.BookController.add_book",
                "module.add_book",
                "module.AddBookRequest",
                "module.Book",
                "module.book_data",
                "module.generate_unique_key",
            ],
        ),
        IntentSpec(
            queries=[
                "get_all_books",
                "all_books_data",
                "book_data",
                "BookController",
                "get_books",
            ],
            expected=[
                "module.BookController.get_all_books",
                "module.get_all_books",
                "module.all_books_data",
                "module.book_data",
            ],
        ),
        IntentSpec(
            queries=[
                "get_book_by_id",
                "book_lookup",
                "book_data",
                "BookController",
                "fetch_book",
            ],
            expected=[
                "module.BookController.get_book_by_id",
                "module.get_book_by_id",
                "module.book_data",
            ],
        ),
        IntentSpec(
            queries=[
                "update_book",
                "BookController",
                "UpdateBookRequest",
                "edit_book",
                "patch_book",
            ],
            expected=[
                "module.BookController.update_book",
                "module.update_book",
                "module.UpdateBookRequest",
            ],
        ),
        IntentSpec(
            queries=[
                "delete_book",
                "BookController",
                "remove_book",
                "drop_book",
                "delete_record",
            ],
            expected=[
                "module.BookController.delete_book",
                "module.delete_book",
            ],
        ),
        IntentSpec(
            queries=[
                "book_schema",
                "AddBookRequest",
                "Book",
                "UpdateBookRequest",
                "book_models",
            ],
            expected=[
                "backend.src.schemas.book_schema",
                "module.AddBookRequest",
                "module.Book",
                "module.UpdateBookRequest",
            ],
        ),
        IntentSpec(
            queries=[
                "app_entrypoint",
                "root",
                "user_route",
                "book_route",
                "FastAPI_app",
            ],
            expected=[
                "backend.main",
                "module.root",
                "backend.src.routes.user_route",
                "backend.src.routes.book_route",
            ],
        ),
    ]


def build_records(specs: list[IntentSpec]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for spec in specs:
        if len(spec.queries) != 5:
            raise ValueError("Each intent must have exactly 5 queries")
        for query in spec.queries:
            records.append({"query": query, "expected": spec.expected})
    return records


def validate_records(records, available_targets: set[str]) -> None:
    if len(records) != 100:
        raise ValueError(f"Expected exactly 100 records, found {len(records)}")

    missing: dict[str, list[int]] = {}
    for index, record in enumerate(records, start=1):
        for target in record["expected"]:
            if target not in available_targets:
                missing.setdefault(target, []).append(index)

    if missing:
        details = ", ".join(
            f"{target} (records {indices})" for target, indices in missing.items()
        )
        raise ValueError(f"Unknown expected targets: {details}")


def write_jsonl(records: list[dict[str, object]], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a 100-item RAG evaluation dataset."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=CHUNK_INDEX_PATH,
        help="Path to the chunk index JSONL file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path to write the dataset JSONL file.",
    )
    parser.add_argument(
        "--style",
        choices=("symbolic", "natural"),
        default="symbolic",
        help="Choose symbolic identifier-style queries or natural-language prompts.",
    )
    args = parser.parse_args()

    available_targets = load_target_index(args.input)
    specs = (
        build_symbolic_specs()
        if args.style == "symbolic"
        else build_natural_language_specs()
    )
    records = build_records(specs)
    validate_records(records, available_targets)
    write_jsonl(records, args.output)
    print(f"Wrote {len(records)} records to {args.output}")


if __name__ == "__main__":
    main()
