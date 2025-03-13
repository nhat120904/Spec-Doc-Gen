from langchain.prompts import PromptTemplate

# Create overview prompt template
overview_prompt = PromptTemplate(
    input_variables=["languages", "components", "code_samples"],
    template="""
    You are a software documentation specialist. Based on the code analysis provided, 
    generate a comprehensive software overview document. Include:

    1. Introduction and Purpose
    2. System Architecture Overview
    3. Technologies Used
    4. Key Components and Their Functions
    5. Data Flow Description
    6. Integration Points
    7. Development and Deployment Considerations

    Languages detected: {languages}
    
    Key components identified:
    {components}
    
    Code samples from key components:
    {code_samples}
    
    Please format the document in Markdown. Be factual and concise while providing 
    meaningful insights about the software's purpose and design.
    """
)

# Create component prompt template
component_prompt = PromptTemplate(
    input_variables=["file_path", "language", "code"],
    template="""
    You are a software specification writer. For the following code, provide:
    
    1. Component Name: (derived from filename or clear purpose in code)
    2. Component Type: (module, class, utility, API, etc.)
    3. Primary Functionality: (brief description of what this component does)
    4. Public Interface: (key methods/functions/endpoints with parameters and return types)
    5. Dependencies: (what other components does this rely on)
    6. Data Structures: (key data structures used or defined)
    7. Error Handling: (how errors are handled if present)
    8. Notes: (any important implementation details or considerations)
    
    File path: {file_path}
    Language: {language}
    
    Code:
    ```
    {code}
    ```
    
    Format your response as Markdown with appropriate headers and code blocks.
    Focus on understanding the code's purpose rather than rewriting the implementation.
    """
)

# Create the integration section based on overall codebase understanding
integration_prompt = PromptTemplate(
    input_variables=["components", "project_structure"],
    template="""
    Based on the component analyses provided, create a comprehensive integration analysis
    showing how these components work together. Include:
    
    1. System Architecture
    2. Component Interaction Diagram (described in text)
    3. Data Flow
    4. Key Integration Points
    5. Dependencies and Their Management
    6. API Contracts (if applicable)
    7. System Requirements
    8. Deployment Architecture
    
    Component analyses:
    {components}
    
    Project structure:
    {project_structure}
    
    Format your response as Markdown with appropriate headers and diagrams described in text.
    """
)