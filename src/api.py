from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sys
import importlib
import traceback
from pathlib import Path

# Add project root to path for compiler imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "output"))

from src.compiler.lexer import Lexer
from src.compiler.parser import Parser
from src.compiler.semantic_analyzer import SemanticAnalyzer
from src.compiler.generator import CodeGenerator

app = FastAPI(title="Password Policy Compiler API")

# Cache to store instantiated validators
VALIDATOR_CACHE = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompileRequest(BaseModel):
    policy_text: str

class ValidateRequest(BaseModel):
    policy_name: str
    password: str

@app.post("/api/compile")
async def compile_policy(request: CompileRequest):
    content = request.policy_text
    
    # Setup tools
    lexer = Lexer()
    lexer.build()
    
    parser = Parser()
    parser.build()
    
    # 1. Lexical Analysis
    lexer.tokenize(content)
    if lexer.errors:
        return {"status": "error", "message": "Lexical errors found", "errors": lexer.errors}

    # 2. Parsing
    ast = parser.parse(content, lexer.lexer)
    if parser.errors:
        return {"status": "error", "message": "Syntax errors found", "errors": parser.errors}
    
    if not ast or not ast.policies:
        return {"status": "error", "message": "No policy found in input", "errors": []}
    
    # Use first policy name
    policy_name = ast.policies[0].name
    
    # 3. Semantic Analysis
    semantic_analyzer = SemanticAnalyzer()
    is_valid, semantic_errors = semantic_analyzer.analyze(ast)
    if semantic_errors:
        return {"status": "error", "message": "Semantic errors found", "errors": semantic_errors}
    
    # 4. Code Generation
    generator = CodeGenerator()
    generated_code = generator.generate(ast)
    if generator.errors:
        return {"status": "error", "message": "Code generation errors", "errors": generator.errors}
        
    # Save the validator class
    output_dir = PROJECT_ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    
    module_name = f"{policy_name.lower()}_validator"
    output_path = output_dir / f"{module_name}.py"
    
    try:
        with open(output_path, "w") as f:
            f.write(generated_code)
            
        # Invalidate cache for this policy so it reloads on next validation
        if policy_name in VALIDATOR_CACHE:
            del VALIDATOR_CACHE[policy_name]
            
        # Also remove from sys.modules so it actually gets reimported
        if module_name in sys.modules:
            del sys.modules[module_name]
            
    except Exception as e:
        return {"status": "error", "message": f"Failed to save validator: {str(e)}"}
        
    return {
        "status": "success", 
        "policy_name": policy_name,
        "message": f"Successfully compiled policy: {policy_name}"
    }

@app.post("/api/validate")
async def validate_password(request: ValidateRequest):
    policy_name = request.policy_name
    password = request.password
    
    module_name = f"{policy_name.lower()}_validator"
    
    try:
        if policy_name in VALIDATOR_CACHE:
            validator = VALIDATOR_CACHE[policy_name]
        else:
            # Check if file exists
            validator_path = PROJECT_ROOT / "output" / f"{module_name}.py"
            if not validator_path.exists():
                return {
                    "status": "error",
                    "message": f"Validator for {policy_name} not found. Please compile it first."
                }
                
            module = importlib.import_module(module_name)
            
            # The class name is typically Capitalized policyname + "Validator"
            class_name = f"{policy_name.capitalize()}Validator"
            if not hasattr(module, class_name):
                class_name = f"{policy_name}Validator"
                
            validator_class = getattr(module, class_name)
            validator = validator_class()
            VALIDATOR_CACHE[policy_name] = validator
        
        # Call validation method (which should return a tuple of len 4 when include_strength=True)
        # Expected return: (is_valid, error_message, strength, entropy)
        result = validator.validate(password, include_strength=True)
        
        if len(result) == 4:
            is_valid, err_msg, strength, entropy = result
            return {
                "status": "success",
                "is_valid": is_valid,
                "message": err_msg,
                "strength": strength,
                "entropy": entropy
            }
        elif len(result) == 2:
            is_valid, err_msg = result
            # Try to get them separately if validate doesn't return them directly
            strength = validator.classify_strength(password) if hasattr(validator, 'classify_strength') else "Unknown"
            entropy = validator.calculate_entropy(password) if hasattr(validator, 'calculate_entropy') else 0.0
            return {
                "status": "success",
                "is_valid": is_valid,
                "message": err_msg,
                "strength": strength,
                "entropy": entropy
            }
        else:
            raise ValueError("Unexpected return format from validate method")
            
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files at root
web_dir = PROJECT_ROOT / "src" / "web"
web_dir.mkdir(exist_ok=True, parents=True)
app.mount("/", StaticFiles(directory=str(web_dir), html=True), name="web")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
