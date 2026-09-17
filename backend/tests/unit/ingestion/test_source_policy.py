"""Source-file policy decides which ZIP members may become indexed text."""

from codebase_assistant.ingestion.source_policy import classify_source_file


def test_accepts_allowlisted_python_source() -> None:
    decision = classify_source_file("src/app.py", b"print(1)\n")
    assert decision.accepted is True
    assert decision.text == "print(1)\n"
    assert decision.reason == "accepted"


def test_nested_env_file_never_returns_contents() -> None:
    decision = classify_source_file("config/.env.production", b"SECRET=super-secret\n")
    assert decision.accepted is False
    assert decision.reason == "secret_file"
    assert decision.text is None


def test_private_key_and_credentials_are_ignored() -> None:
    key = classify_source_file(
        "deploy/id_rsa",
        b"-----BEGIN OPENSSH PRIVATE KEY-----\n",
    )
    pem = classify_source_file("certs/site.pem", b"-----BEGIN CERTIFICATE-----\n")
    creds = classify_source_file("app/credentials.json", b'{"password":"x"}')
    assert key.accepted is False and key.text is None
    assert pem.accepted is False and pem.text is None
    assert creds.accepted is False and creds.text is None


def test_dependency_and_build_directories_are_ignored() -> None:
    node = classify_source_file(
        "frontend/node_modules/leftpad/index.js",
        b"module.exports=1\n",
    )
    git = classify_source_file(".git/config", b"[core]\n")
    dist = classify_source_file("frontend/dist/bundle.js", b"console.log(1)\n")
    cache = classify_source_file("backend/__pycache__/app.cpython-314.pyc", b"\x00")
    assert node.reason == "excluded_directory"
    assert git.reason == "excluded_directory"
    assert dist.reason == "excluded_directory"
    assert cache.reason == "excluded_directory"
    assert node.text is None


def test_disallowed_extension_is_ignored() -> None:
    decision = classify_source_file("notes.docx", b"PK")
    assert decision.accepted is False
    assert decision.reason == "extension"


def test_nul_bytes_are_treated_as_binary() -> None:
    decision = classify_source_file("src/app.py", b"print(1)\n\x00\xff")
    assert decision.accepted is False
    assert decision.reason == "binary"
    assert decision.text is None


def test_invalid_utf8_does_not_crash() -> None:
    decision = classify_source_file("readme.md", b"\xff\xfe not utf-8")
    assert decision.accepted is False
    assert decision.reason == "encoding"
    assert decision.text is None


def test_generated_lockfiles_are_ignored_without_returning_contents() -> None:
    lockfiles = (
        "frontend/package-lock.json",
        "npm-shrinkwrap.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "Cargo.lock",
        "poetry.lock",
        "composer.lock",
        "go.sum",
        "Pipfile.lock",
    )
    payload = b'{"packages":{"chalk":{"version":"4.0.0"}}}\n'
    for path in lockfiles:
        decision = classify_source_file(path, payload)
        assert decision.accepted is False, path
        assert decision.reason == "generated_lockfile", path
        assert decision.text is None, path


def test_minified_bundles_are_ignored() -> None:
    js = classify_source_file("static/app.min.js", b"function x(){}\n")
    css = classify_source_file("assets/theme.min.css", b"body{color:red}\n")
    assert js.accepted is False
    assert js.reason == "generated_bundle"
    assert js.text is None
    assert css.accepted is False
    assert css.reason == "generated_bundle"
    assert css.text is None


def test_declared_manifests_and_readme_remain_indexed() -> None:
    package = classify_source_file(
        "frontend/package.json",
        b'{"name":"school-crm","dependencies":{"react":"18.2.0"}}\n',
    )
    pyproject = classify_source_file(
        "pyproject.toml",
        b'[project]\nname = "inventory"\ndependencies = ["fastapi"]\n',
    )
    requirements = classify_source_file("requirements.txt", b"fastapi==0.141.1\n")
    readme = classify_source_file("README.md", b"# Inventory service\n")
    source = classify_source_file("src/app.js", b"export const n = 1\n")
    assert package.accepted and package.reason == "accepted"
    assert pyproject.accepted and pyproject.reason == "accepted"
    assert requirements.accepted and requirements.reason == "accepted"
    assert readme.accepted and readme.reason == "accepted"
    assert source.accepted and source.reason == "accepted"
