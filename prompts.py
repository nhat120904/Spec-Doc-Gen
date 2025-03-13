from langchain.prompts import PromptTemplate

# Overview document prompt
overview_prompt = PromptTemplate(
    input_variables=["languages", "components", "code_samples"],
    template="""
    You are a software documentation specialist. Based on the code analysis provided, 
    generate a comprehensive software overview document in JSON format. Include:

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
    
    Return ONLY a valid JSON object with the following structure:
    {{
      "introduction": "Text describing the purpose...",
      "architecture": "Text describing system architecture...",
      "technologies": ["tech1", "tech2", ...],
      "components": [
        {{
          "name": "Component name",
          "description": "Component description",
          "responsibilities": ["Responsibility 1", ...]
        }}
      ],
      "dataFlow": "Text describing data flow...",
      "integrationPoints": ["Point 1", ...],
      "developmentConsiderations": "Text describing development considerations..."
    }}
    """
)

# Component analysis prompt
component_prompt = PromptTemplate(
    input_variables=["file_path", "language", "code"],
    template="""
    You are a software specification writer. For the following code, analyze the component and return a JSON object:
    
    File path: {file_path}
    Language: {language}
    
    Code:
    ```
    {code}
    ```
    
    Return ONLY a valid JSON object with the following structure:
    {{
      "componentName": "Derived from filename or clear purpose in code",
      "componentType": "module/class/utility/API/etc.",
      "primaryFunctionality": "Brief description of what this component does",
      "publicInterface": [
        {{
          "name": "methodName",
          "parameters": ["param1:type", "param2:type"],
          "returnType": "return type",
          "description": "what the method does"
        }}
      ],
      "dependencies": ["dependency1", "dependency2"],
      "dataStructures": [
        {{
          "name": "structureName",
          "fields": ["field1:type", "field2:type"],
          "purpose": "what this structure is used for"
        }}
      ],
      "errorHandling": "Description of error handling if present",
      "notes": "Any important implementation details"
    }}
    """
)

# Integration analysis prompt
integration_prompt = PromptTemplate(
    input_variables=["components", "project_structure"],
    template="""
    Based on the component analyses provided, create a comprehensive integration analysis
    showing how these components work together. Return the analysis as a JSON object.
    
    Component analyses:
    {components}
    
    Project structure:
    {project_structure}
    
    Return ONLY a valid JSON object with the following structure:
    {{
      "systemArchitecture": "Description of overall architecture",
      "componentInteractions": [
        {{
          "source": "Component A",
          "target": "Component B",
          "description": "How A interacts with B"
        }}
      ],
      "dataFlow": "Description of data flow through the system",
      "integrationPoints": [
        {{
          "name": "Integration point name",
          "description": "Description of this integration point"
        }}
      ],
      "dependencies": {{"component": ["dependency1", "dependency2"]}},
      "apiContracts": [
        {{
          "endpoint": "API endpoint",
          "method": "HTTP method",
          "parameters": ["param1", "param2"],
          "response": "Response description"
        }}
      ],
      "systemRequirements": ["requirement1", "requirement2"],
      "deploymentArchitecture": "Description of deployment architecture"
    }}
    """
)