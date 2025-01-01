import hashlib
import ast
import time
from typing import Dict, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
import pandas as pd
import os

class SubmissionType(Enum):
    CODE = "code"
    DATASET = "dataset"
    CODE_AND_DATASET = "code_and_dataset"

class SubmissionStatus(Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class BlockchainMetadata:
    block_number: int
    timestamp: int
    gas_used: int
    transaction_hash: str

class AISubmission:
    def __init__(self, 
                 wallet_address: str,
                 code: Optional[str] = None, 
                 dataset: Optional[str] = None,
                 submission_type: SubmissionType = SubmissionType.CODE):
        self.wallet_address = wallet_address
        self.code = code
        self.dataset = dataset
        self.submission_type = submission_type
        self.timestamp = int(time.time())
        self.submission_hash = self._generate_hash()
        self.status = SubmissionStatus.PENDING
        self.blockchain_metadata: Optional[BlockchainMetadata] = None

    def _generate_hash(self) -> str:
        """Generate a unique hash for this submission"""
        content = f"{self.wallet_address}{self.code or ''}{self.dataset or ''}{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return {
            'wallet_address': self.wallet_address,
            'submission_hash': self.submission_hash,
            'code': self.code,
            'dataset': self.dataset,
            'submission_type': self.submission_type.value,
            'timestamp': self.timestamp,
            'status': self.status.value
        }

def verify_code_syntax(code: str) -> Tuple[bool, str]:
    """Verify that the submitted code is valid Python syntax"""
    try:
        ast.parse(code)
        
        # Check for required functions
        tree = ast.parse(code)
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        if 'predict' not in functions:
            return False, "Missing required 'predict' function"
        
        return True, "Code syntax is valid"
    except SyntaxError as e:
        return False, f"Syntax error: {str(e)}"

def verify_dataset(dataset: str) -> Tuple[bool, str]:
    """Verify that the dataset is valid CSV format with required columns"""
    try:
        df = pd.read_csv(pd.StringIO(dataset))
        required_columns = ['GRE Score', 'TOEFL Score', 'University Rating', 
                          'SOP', 'LOR', 'CGPA', 'Research', 'Chance of Admit']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return False, f"Missing required columns: {missing_columns}"
            
        return True, "Dataset format is valid"
    except Exception as e:
        return False, f"Dataset validation error: {str(e)}"

def submit_to_blockchain(wallet_address: str, 
                        code: Optional[str] = None, 
                        dataset: Optional[str] = None) -> Dict:
    """Submit AI code and optional dataset to the blockchain"""
    
    # Determine submission type
    if code and dataset:
        submission_type = SubmissionType.CODE_AND_DATASET
    elif code:
        submission_type = SubmissionType.CODE
    elif dataset:
        submission_type = SubmissionType.DATASET
    else:
        raise ValueError("Must provide either code or dataset")

    # Create submission
    submission = AISubmission(
        wallet_address=wallet_address,
        code=code,
        dataset=dataset,
        submission_type=submission_type
    )

    # Verify submission contents
    verification_results = []
    
    if code:
        is_valid, message = verify_code_syntax(code)
        verification_results.append(('code', is_valid, message))
    
    if dataset:
        is_valid, message = verify_dataset(dataset)
        verification_results.append(('dataset', is_valid, message))

    # Check if any verifications failed
    failed_verifications = [result for result in verification_results if not result[1]]
    if failed_verifications:
        error_messages = [f"{result[0]}: {result[2]}" for result in failed_verifications]
        return {
            'status': 'error',
            'errors': error_messages,
            'submission': submission.to_dict()
        }

    # Here you would actually submit to the blockchain
    # For now, simulate blockchain metadata
    submission.blockchain_metadata = BlockchainMetadata(
        block_number=1000,
        timestamp=submission.timestamp,
        gas_used=21000,
        transaction_hash=hashlib.sha256(str(time.time()).encode()).hexdigest()
    )
    
    return {
        'status': 'success',
        'submission': submission.to_dict(),
        'blockchain_metadata': {
            'block_number': submission.blockchain_metadata.block_number,
            'timestamp': submission.blockchain_metadata.timestamp,
            'gas_used': submission.blockchain_metadata.gas_used,
            'transaction_hash': submission.blockchain_metadata.transaction_hash
        }
    }

def get_submission_status(submission_hash: str) -> Dict:
    """Get the status of a submission from the blockchain"""
    # This would actually query the blockchain
    # For now, return simulated status
    return {
        'submission_hash': submission_hash,
        'status': SubmissionStatus.PENDING.value,
        'last_updated': int(time.time()),
        'execution_results': None
    }

def perform_ai_work(submitted_code: str, dataset: Optional[str] = None) -> Dict:
    """
    Executes the submitted code against test data.
    Returns the execution results.
    """
    try:
        # Create a temporary file for the code
        with open('temp_ai_code.py', 'w') as f:
            f.write(submitted_code)
        
        # Load and validate the code
        is_valid, message = verify_code_syntax(submitted_code)
        if not is_valid:
            return {'status': 'error', 'message': message}
        
        # If dataset provided, validate it
        if dataset:
            is_valid, message = verify_dataset(dataset)
            if not is_valid:
                return {'status': 'error', 'message': message}
            
            # Save dataset temporarily
            with open('temp_dataset.csv', 'w') as f:
                f.write(dataset)
        
        # Simulate some coefficients for blockchain verification
        coefficients = [0.9281502425863708, 0.8418398385575229]
        
        # Return in format expected by blockchain
        return {
            'status': 'success',
            'message': 'Code execution completed',
            'coefficients': coefficients,  # Move coefficients to top level
            'result': {
                'execution_time': time.time(),
                'output': 'Simulated output'
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Execution error: {str(e)}'
        }
    finally:
        # Cleanup temporary files
        if os.path.exists('temp_ai_code.py'):
            os.remove('temp_ai_code.py')
        if os.path.exists('temp_dataset.csv'):
            os.remove('temp_dataset.csv')

def verify_ai_work(ai_task: Dict, ai_solution: Dict) -> Tuple[bool, Dict]:
    """
    Verifies if the provided AI solution meets the required criteria.
    """
    if 'coefficients' not in ai_solution:
        return False, {'error': 'Missing required coefficients'}
    
    # Extract coefficients from the solution
    coefficients = ai_solution['coefficients']
    
    # Here you would implement actual verification logic
    # For now, just check if coefficients exist
    return True, {
        'message': 'AI work verified successfully',
        'coefficients': coefficients
    }

