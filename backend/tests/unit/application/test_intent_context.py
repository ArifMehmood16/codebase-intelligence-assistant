"""Intent-routed context pins README/manifests for overview questions (PLAN 13.5)."""

import io
import zipfile

from codebase_assistant.adapters.extractive import ExtractiveCompleter
from codebase_assistant.adapters.lexical import LexicalEmbedder
from codebase_assistant.adapters.memory import InMemoryWorkspace
from codebase_assistant.application.ask import ask_question
from codebase_assistant.application.contracts import (
    AskQuestionRequest,
    IngestArchiveRequest,
)
from codebase_assistant.application.ingest import ingest_archive
from codebase_assistant.chunking import ChunkingLimits
from codebase_assistant.ingestion.limits import ArchiveLimits

_LIMITS = ArchiveLimits(max_upload_bytes=1024 * 1024)
_CHUNKS = ChunkingLimits(max_lines=40, overlap_lines=0)


def _zip_bytes(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def _ingest(members: dict[str, bytes], filename: str = "repo.zip") -> tuple:
    workspace = InMemoryWorkspace()
    embed = LexicalEmbedder()
    ingested = ingest_archive(
        IngestArchiveRequest(filename=filename, content=_zip_bytes(members)),
        archive_limits=_LIMITS,
        chunk_limits=_CHUNKS,
        embed=embed,
        store=workspace,
    )
    return workspace, embed, ingested


def test_overview_question_cites_readme_not_noisy_json() -> None:
    noise = (
        b"what does this repo do? this repo does what this repo does. "
        b"what does this repo do? chalk rollup follow-redirects is-callable.\n"
    ) * 20
    workspace, embed, ingested = _ingest(
        {
            "README.md": b"# Inventory service\nStores warehouse stock items.\n",
            "meta/packages.json": noise,
        }
    )
    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="what does this repo do?",
        ),
        embed=embed,
        search=workspace,
        complete=ExtractiveCompleter(),
    )
    cited = {citation.file_path for citation in answer.answer.citations}
    assert answer.answer.insufficient_evidence is False
    assert "README.md" in cited
    assert "meta/packages.json" not in cited


def test_locate_question_still_uses_vector_hits() -> None:
    workspace, embed, ingested = _ingest(
        {
            "README.md": b"# Demo\n",
            "src/app.py": b"def greet():\n    return 'hello'\n",
        }
    )
    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="Where is greet defined?",
        ),
        embed=embed,
        search=workspace,
        complete=ExtractiveCompleter(),
    )
    assert answer.answer.citations[0].file_path == "src/app.py"
    assert "greet" in answer.answer.text


def test_endpoints_question_lists_extracted_routes_from_card() -> None:
    class BoomCompleter:
        def complete(self, prompt: str) -> str:
            raise AssertionError("endpoint answers must list extracted card routes")

    workspace, embed, ingested = _ingest(
        {
            "src/api/handlers.py": (
                b'def list_items():\n    """Return items for GET /items."""\n'
                b"    return []\n\n"
                b'def create_item():\n    """Create an item for POST /items."""\n'
                b"    return {}\n"
            ),
            "src/api/ItemController.py": (
                b"class ItemController:\n"
                b"    def get_items(self):\n"
                b'        """GET /items - controller entry."""\n'
                b"        return []\n"
            ),
        }
    )
    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="What API endpoints exist?",
        ),
        embed=embed,
        search=workspace,
        complete=BoomCompleter(),
    )
    text = answer.answer.text
    cited = {citation.file_path for citation in answer.answer.citations}
    assert answer.answer.insufficient_evidence is False
    assert "GET /items" in text
    assert "POST /items" in text
    assert "src/api/handlers.py" in cited
    assert "src/api/handlers.py" in text


def test_endpoints_question_cites_handler_not_noisy_json() -> None:
    noise = (
        b"GET /items POST /items api endpoints routes handlers controllers.\n"
    ) * 30
    workspace, embed, ingested = _ingest(
        {
            "src/api/handlers.py": (
                b'def list_items():\n    """Return items for GET /items."""\n'
                b"    return []\n\n"
                b'def create_item():\n    """Create an item for POST /items."""\n'
                b"    return {}\n"
            ),
            "meta/packages.json": noise,
        }
    )
    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="What API endpoints exist for items?",
        ),
        embed=embed,
        search=workspace,
        complete=ExtractiveCompleter(),
    )
    cited = {citation.file_path for citation in answer.answer.citations}
    assert ingested.card is not None
    routes = {(item.method, item.path) for item in ingested.card.endpoints}
    assert ("GET", "/items") in routes
    assert ("POST", "/items") in routes
    assert answer.answer.insufficient_evidence is False
    assert "src/api/handlers.py" in cited
    assert "meta/packages.json" not in cited


def test_structure_question_shows_directory_tree_and_readme_context() -> None:
    class BoomCompleter:
        def complete(self, prompt: str) -> str:
            raise AssertionError("structure answers must use the derived outline")

    workspace, embed, ingested = _ingest(
        {
            "README.md": b"# Inventory service\nStores warehouse stock items.\n",
            "src/app.py": b"def greet():\n    return 1\n",
            "src/api/handlers.py": b"def list_items():\n    return []\n",
        }
    )
    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="What is the structure of this repo?",
        ),
        embed=embed,
        search=workspace,
        complete=BoomCompleter(),
    )
    text = answer.answer.text
    assert answer.answer.insufficient_evidence is False
    assert "### Directory structure" in text
    assert "```tree" in text
    assert "README.md" in text
    assert "src/" in text
    assert "  api/" in text
    assert "    handlers.py" in text
    assert "Stores warehouse stock items" in text
    cited = {citation.file_path for citation in answer.answer.citations}
    assert cited & {"README.md", "src/app.py", "src/api/handlers.py"}


def test_structure_without_readme_still_shows_tree() -> None:
    class BoomCompleter:
        def complete(self, prompt: str) -> str:
            raise AssertionError("structure answers must use the derived outline")

    workspace, embed, ingested = _ingest({"src/app.py": b"x = 1\n"})
    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="What is the directory structure?",
        ),
        embed=embed,
        search=workspace,
        complete=BoomCompleter(),
    )
    assert answer.answer.insufficient_evidence is False
    assert "src/" in answer.answer.text
    assert "app.py" in answer.answer.text
    assert "Cited indexed file" in answer.answer.text
    assert answer.answer.citations[0].file_path == "src/app.py"


def test_overview_without_readme_or_manifest_is_insufficient() -> None:
    class BoomCompleter:
        def complete(self, prompt: str) -> str:
            raise AssertionError("must not complete overview without README/manifest")

    workspace, embed, ingested = _ingest(
        {"src/app.py": b"def greet():\n    return 'hello endpoints exist'\n"}
    )
    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="what does this repo do?",
        ),
        embed=embed,
        search=workspace,
        complete=BoomCompleter(),
    )
    assert answer.answer.insufficient_evidence is True
    assert answer.answer.citations == ()


def test_endpoints_without_extracted_routes_is_insufficient() -> None:
    class BoomCompleter:
        def complete(self, prompt: str) -> str:
            raise AssertionError("must not invent endpoints from unrelated source")

    workspace, embed, ingested = _ingest(
        {"src/app.py": b"def greet():\n    return 'hello endpoints exist'\n"}
    )
    assert ingested.card is not None
    assert ingested.card.endpoints == ()
    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="What API endpoints exist?",
        ),
        embed=embed,
        search=workspace,
        complete=BoomCompleter(),
    )
    assert answer.answer.insufficient_evidence is True
    assert answer.answer.citations == ()


def test_dependencies_without_manifest_is_insufficient() -> None:
    class BoomCompleter:
        def complete(self, prompt: str) -> str:
            raise AssertionError("must not invent dependencies without a manifest")

    workspace, embed, ingested = _ingest(
        {"src/app.py": b"import json\nLIBRARIES = ['fastapi']\n"}
    )
    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="What dependencies does this project declare?",
        ),
        embed=embed,
        search=workspace,
        complete=BoomCompleter(),
    )
    assert answer.answer.insufficient_evidence is True
    assert answer.answer.citations == ()


def test_architecture_flow_pins_deep_layer_files() -> None:
    root = "src/main/java/org/example/owner"
    workspace, _embed, ingested = _ingest(
        {
            f"{root}/OwnerController.java": (
                b"class OwnerController {\n"
                b"  private OwnerService owners;\n"
                b"  void save(Owner owner) { owners.save(owner); }\n"
                b"}\n"
            ),
            f"{root}/PetController.java": (
                b"class PetController {\n"
                b"  private OwnerRepository owners;\n"
                b"  void save(Pet pet) { owners.save(pet.getOwner()); }\n"
                b"}\n"
            ),
            f"{root}/OwnerService.java": (
                b"class OwnerService { OwnerRepository owners; }\n"
            ),
            f"{root}/OwnerRepository.java": (
                b"interface OwnerRepository extends Repository<Owner, Integer> {}\n"
            ),
            "src/main/java/org/example/domain/Owner.java": (
                b"@Entity class Owner {}\n"
            ),
            "src/main/resources/schema.sql": b"create table owners (id integer);\n",
        },
        filename="petclinic.zip",
    )

    class NoQueryEmbedding:
        def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
            raise AssertionError("architecture flow must use exact path lookup")

    class RecordingCompleter:
        def complete(self, prompt: str) -> str:
            assert "OwnerController.java" in prompt
            assert "PetController.java" in prompt
            assert "OwnerService.java" in prompt
            assert "OwnerRepository.java" in prompt
            assert "Owner.java" in prompt
            assert "schema.sql" in prompt
            assert "one section per controller" in prompt
            return (
                '{"text":"OwnerController.save → OwnerService.save → '
                "OwnerRepository.save → Owner → database [1] "
                'PetController → OwnerRepository → Owner → database",'
                '"citations":[{"file_path":"'
                f"{root}/OwnerController.java"
                '","start_line":1,"end_line":4}],"insufficient_evidence":false}'
            )

    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question=(
                "What is the end to end logic path from controller to database "
                "for all controllers?"
            ),
        ),
        embed=NoQueryEmbedding(),
        search=workspace,
        complete=RecordingCompleter(),
    )
    assert answer.answer.insufficient_evidence is False
    assert answer.answer.citations[0].file_path.endswith("OwnerController.java")
    assert "### OwnerController" in answer.answer.text
    assert "### PetController" in answer.answer.text
    assert answer.answer.text.count("**Flow:**") == 2
    assert "**Method-level detail:** Not evidenced" in answer.answer.text
    assert answer.answer.text.startswith("This repository")


def test_architecture_flow_without_controller_source_is_insufficient() -> None:
    class BoomCompleter:
        def complete(self, prompt: str) -> str:
            raise AssertionError("must not invent controller flows")

    path = "src/main/java/org/example/OwnerRepository.java"
    workspace, embed, ingested = _ingest({path: b"interface OwnerRepository {}\n"})
    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="Trace the controller to database flow",
        ),
        embed=embed,
        search=workspace,
        complete=BoomCompleter(),
    )
    assert answer.answer.insufficient_evidence is True
    assert answer.answer.citations == ()


def test_named_controller_question_pins_every_controller_chunk() -> None:
    filler = [f"  // line {line}" for line in range(1, 86)]
    filler[4] = "  void loadPetWithVisit() { ownerRepository.findById(1); }"
    filler[49] = "  void initNewVisitForm() { pet.addVisit(new Visit()); }"
    filler[81] = "  void processNewVisitForm() { ownerRepository.save(owner); }"
    visit_source = ("class VisitController {\n" + "\n".join(filler) + "\n}\n").encode()
    workspace, _embed, ingested = _ingest(
        {
            "src/owner/VisitController.java": visit_source,
            "src/owner/OwnerController.java": b"class OwnerController {}\n",
        }
    )

    class NoQueryEmbedding:
        def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
            raise AssertionError("named controller lookup must use exact paths")

    class RecordingCompleter:
        def complete(self, prompt: str) -> str:
            assert "loadPetWithVisit" in prompt
            assert "initNewVisitForm" in prompt
            assert "processNewVisitForm" in prompt
            assert "OwnerController.java" not in prompt
            assert "all available chunks" in prompt.lower()
            return (
                '{"text":"VisitController manages visit form setup and saving. '
                "It has 3 evidenced methods.\\n\\n| Method | Route / trigger | "
                "Purpose | "
                "Collaborators / entities |\\n| --- | --- | --- | --- |\\n| "
                "loadPetWithVisit | model setup | Loads the pet | "
                "OwnerRepository [1] |\\n| initNewVisitForm | GET form | Creates a "
                "visit | Pet, Visit [1] |\\n| processNewVisitForm | POST form | "
                'Saves a visit | OwnerRepository, Visit [1] |",'
                '"citations":[{"file_path":"src/owner/VisitController.java",'
                '"start_line":1,"end_line":40}],"insufficient_evidence":false}'
            )

    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question=(
                "what does visit controller do? how many method in there? "
                "what is their purpose each. give me table"
            ),
        ),
        embed=NoQueryEmbedding(),
        search=workspace,
        complete=RecordingCompleter(),
    )
    assert answer.answer.insufficient_evidence is False
    assert "It has 3 evidenced methods" in answer.answer.text
    assert "| Method | Route / trigger | Purpose |" in answer.answer.text


def test_named_controller_question_is_insufficient_when_controller_is_absent() -> None:
    class BoomCompleter:
        def complete(self, prompt: str) -> str:
            raise AssertionError("must not answer from a different controller")

    workspace, embed, ingested = _ingest(
        {"src/owner/OwnerController.java": b"class OwnerController {}\n"}
    )
    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="What does VisitController do? List its methods",
        ),
        embed=embed,
        search=workspace,
        complete=BoomCompleter(),
    )
    assert answer.answer.insufficient_evidence is True
    assert answer.answer.citations == ()


def test_named_code_unit_rejects_flat_partial_inventory() -> None:
    workspace, embed, ingested = _ingest(
        {
            "src/owner/VisitController.java": (
                b"class VisitController {\n"
                b"  void loadPetWithVisit() {}\n"
                b"  void processNewVisitForm() {}\n"
                b"}\n"
            )
        }
    )

    class FlatCompleter:
        def complete(self, prompt: str) -> str:
            return (
                '{"text":"VisitController has two methods: loadPetWithVisit and '
                'processNewVisitForm.","citations":[{"file_path":"src/owner/'
                'VisitController.java","start_line":1,"end_line":4}],'
                '"insufficient_evidence":false}'
            )

    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="What does VisitController do? List its methods in a table",
        ),
        embed=embed,
        search=workspace,
        complete=FlatCompleter(),
    )
    assert answer.answer.insufficient_evidence is True
    assert answer.answer.citations == ()


def test_named_code_unit_rejects_count_table_mismatch() -> None:
    workspace, embed, ingested = _ingest(
        {
            "src/owner/VisitController.java": (
                b"class VisitController {\n"
                b"  void loadPetWithVisit() {}\n"
                b"  void processNewVisitForm() {}\n"
                b"}\n"
            )
        }
    )

    class InconsistentCompleter:
        def complete(self, prompt: str) -> str:
            return (
                '{"text":"VisitController manages visits. It has 2 evidenced '
                "methods.\\n\\n| Method | Route / trigger | Purpose | Collaborators "
                "/ entities |\\n| --- | --- | --- | --- |\\n| loadPetWithVisit | "
                'setup | Loads a pet | OwnerRepository [1] |","citations":[{'
                '"file_path":"src/owner/VisitController.java","start_line":1,'
                '"end_line":4}],"insufficient_evidence":false}'
            )

    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="What does VisitController do? List its methods in a table",
        ),
        embed=embed,
        search=workspace,
        complete=InconsistentCompleter(),
    )
    assert answer.answer.insufficient_evidence is True
    assert answer.answer.citations == ()


def test_named_code_unit_lookup_is_not_controller_specific() -> None:
    workspace, _embed, ingested = _ingest(
        {
            "src/services/inventory_service.py": (
                b"def find_by_name(name: str):\n    return name\n"
            ),
            "src/owner/VisitController.java": b"class VisitController {}\n",
        }
    )

    class NoQueryEmbedding:
        def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
            raise AssertionError("named code-unit lookup must use exact paths")

    class RecordingCompleter:
        def complete(self, prompt: str) -> str:
            assert "inventory_service.py" in prompt
            assert "find_by_name" in prompt
            assert "VisitController.java" not in prompt
            return (
                '{"text":"Not enough evidence.","citations":[],'
                '"insufficient_evidence":true}'
            )

    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="What does InventoryService do? List its functions",
        ),
        embed=NoQueryEmbedding(),
        search=workspace,
        complete=RecordingCompleter(),
    )
    assert answer.answer.insufficient_evidence is True


def test_locate_pins_identifier_missing_from_vector_hits() -> None:
    class MissesService(InMemoryWorkspace):
        def search(self, repository_id, embedding, limit):
            hits = super().search(repository_id, embedding, limit)
            return tuple(
                chunk
                for chunk in hits
                if chunk.file_path != "src/services/inventory.py"
            )

    workspace = MissesService()
    embed = LexicalEmbedder()
    ingested = ingest_archive(
        IngestArchiveRequest(
            filename="inventory.zip",
            content=_zip_bytes(
                {
                    "README.md": b"# Inventory\nStores items in memory.\n",
                    "src/services/inventory.py": (
                        b"def find_by_name(name: str):\n    return name\n"
                    ),
                }
            ),
        ),
        archive_limits=_LIMITS,
        chunk_limits=_CHUNKS,
        embed=embed,
        store=workspace,
    )
    answer = ask_question(
        AskQuestionRequest(
            repository_id=ingested.repository.repository_id,
            question="Where is find_by_name implemented?",
        ),
        embed=embed,
        search=workspace,
        complete=ExtractiveCompleter(),
    )
    cited = {citation.file_path for citation in answer.answer.citations}
    blob = " ".join([answer.answer.text, *[item.excerpt for item in answer.excerpts]])
    assert answer.answer.insufficient_evidence is False
    assert "src/services/inventory.py" in cited
    assert "find_by_name" in blob
