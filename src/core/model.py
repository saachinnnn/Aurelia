from enum import Enum
from typing import List,Optional,Annotated,Literal
from pydantic import BaseModel,Field,field_validator,HttpUrl

# So first we are going to be defining the structure of Chunks.
## Each chunks can atmost have the following parameters;
'''
1)module(orphan code)
2)class
3)function
4)method
5)block
'''
# THe above is a custom structure that is used for Aurelia.
# This class is used for serialzing the values of chunk-types.
class ChunkType(str, Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    BLOCK = "block"

# This is for giving various options for file classification that can be used to imply different forms of chunking later on.
class FileClassification(str, Enum):
    PARSE = "parse"
    MARKDOWN = "markdown"
    CONFIG = "config"
    SKIP = "skip"

# Validation schema for the output of walker.py.
class FileInfo(BaseModel):
    absolute_path: str
    relative_path: str
    classification: FileClassification

# Now we are going to define the structure of a chunk.
class ChunkMetadata(BaseModel):
    file_path : str
    language : str 
    line_start : int
    line_end : int
    git_author : Optional[str] = None 
    git_last_modified : Optional[str] = None
    imports : List[str] = [] # I think this means if there is no import then we store an empty list.
    linked_chunks : List[str] = []

# The Below is configuration for llmsetings, embedding settings, retrieval settings, chunking settings

# ----------------------------
# LLM settings (discriminated)
# ----------------------------
## The below is the settings for validation only for Premium Models.
class GeminiSettings(BaseModel):
    provider: Literal["gemini"] = "gemini"
    model : str = Field(default = "gemini-3-flash-preview",min_length = 1)
    api_key : str = Field(default = "")
    temperature : float = Field(default = 0.2,ge = 0.0,le = 0.2)
    top_p : float = Field(default = 1.0,ge = 0.0 ,le = 1.0)
    max_output_tokens : int = Field(default = 512, ge = 1)

    timeout_s : float = Field(default = 60.0,gt = 0.0)
    max_retries : int = Field(default = 2,ge = 0)
    stream : bool = True 

    base_url : Optional[HttpUrl] = None 


## Settings for validation for Free open source models.
class OllamaSettings(BaseModel):
    provider : Literal["ollama"] = "ollama"
    model : str = Field(default = "llama3.2",min_length = 1)
    
    temperature : float = Field(default = 0.2,ge = 0.0,le = 0.2)
    top_p : float = Field(default = 1.0,ge = 0.0 ,le = 1.0)
    max_output_tokens : int = Field(default = 512, ge = 1)

    timeout_s : float = Field(default = 60.0,gt = 0.0)
    max_retries : int = Field(default = 2,ge = 0)
    stream : bool = True 

    base_url : Optional[HttpUrl] = Field(default = "http://localhost:11434") # Runs on local machine.

# Now that we have to LLM's, we annottate the settings into a single setting
LLMSetting = Annotated[
    GeminiSettings | OllamaSettings,
    Field(discriminator="provider") # We call by the valdiated name in the pydantic model
]

# --------------------------------
# Embedding settings (discriminated)
# --------------------------------
class VoyageSettings(BaseModel):
    provider : Literal["voyageai"] = "voyageai"
    model : str = Field(default = "voyage-code-3",min_length = 1)
    api_key : str = Field(default = "")
    batch_size : int = Field(default = 64,ge = 1)
    timeout_s : float = Field(default = 60.0,gt = 0.0)
    dimensions : Optional[int] = Field(default = 1024,gt = 0)
    normalize : bool = Field(default = True) # This can change so I am making this into as a Field

class bgeSettings(BaseModel):
    provider : Literal["bge"] = "bge"
    model : str = Field(default = "BGE-M3",min_length = 1)
    batch_size : int = Field(default = 64,ge = 1)
    timeout_s : float = Field(default = 60.0,gt = 0.0)
    dimensions : int = Field(default = 1024,gt = 0)
    normalize : bool = Field(default = True) # This can change so I am making this into as a Field

# Now that we have the embedding models settings, lets annotate the Premium and the Opensource models as well through the discriminator.
EmbeddingSetting = Annotated[
    VoyageSettings | bgeSettings,
    Field(discriminator="provider")
]   

# ----------------------------
# Retrieval settings
# ----------------------------

# First lets define the different types of modes that can be present in the Retrieval pipeline.
class RetrievalMode(str,Enum):
    SIMILARITY = 'similarity'
    KEYWORD = 'keyword'
    HYBRID = 'hybrid'

# Now we define the options that are available for reranker providers.
class RerankerProvider(str,Enum):
    NONE = "none" # Default setting as reranker is present in the first version.
    CROSS_ENCODER = "cross-encoder" # OpenSource
    GEMINI_RERANKER = "gemini-reranker" # Premium

# Defining the Retrieval Settigns
class RetrievalSettings(BaseModel):
    provider : RerankerProvider = RerankerProvider.NONE # The first version does not have any reranker.
    top_k : int = Field(default = 3,ge = 1,le = 5) # For now.

    mode : RetrievalMode = RetrievalMode.HYBRID
    rerank_top_n : int = Field(default = 3,ge = 1,le = 5) # For now.
    metadata_filter : dict[str,str]  = Field(default_factory = dict)
    # We will write the RRF logic later.

# ----------------------------
# Chunking settings
# ----------------------------
## Extremely Important.

class ChunkingStrategy(str,Enum):
    HIERARCHICAL = "hierarchical" # Default setting as reranker is present in the first version.
    FLAT = "flat"
    # For now, this is going to be the only setting.

class ChunkingSettings(BaseModel):
    strategy : ChunkingStrategy = ChunkingStrategy.HIERARCHICAL
    max_chunk_size : int = Field(default = 512,ge = 10)
    max_overlap : int = Field(default = 75,ge = 0)
    language : str = "python"

    @field_validator("max_overlap")
    @classmethod
    def _validate_overlap(cls,v,info):
        if v >= info.data["max_chunk_size"]:
            raise ValueError("max_overlap must be less than max_chunk_size")
        return v

    @field_validator("language")
    @classmethod
    def _validate_language(cls,v,info):
        if v.lower().strip() != "python":
            raise ValueError("language must be python")
        return v
    # The rest of the validation parameters if needed will be adaed later.

# ----------------------------
# Aurelia Configuration
# ----------------------------

class AureliaConfig(BaseModel):
    """
    Configuration Object for Aurelia.
    Laoding this from YAML/JSON/TOML followed by validation we can pass this to the app.
    """
    llm : LLMSetting = Field(default_factory = GeminiSettings)
    embedding : EmbeddingSetting = Field(default_factory = VoyageSettings)
    retrieval : RetrievalSettings = Field(default_factory = RetrievalSettings)
    chunking : ChunkingSettings = Field(default_factory = ChunkingSettings)

    project_name : str = Field(default = "Aurelia",min_length = 1)
    data_dir : str = Field(default = "./data")

    