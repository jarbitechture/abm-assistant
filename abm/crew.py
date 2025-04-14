# abm/crew.py

import logging
import json
# Corrected import: Ensure Optional is included
from typing import Dict, List, Tuple, Optional

# Use relative imports and config values
from .config import OPENAI_API_KEY, CREWAI_LLM_MODEL, CREWAI_LLM_TEMPERATURE
# We might not need summarize_deal_context here if agents work from raw data
# from .sales_copilot import summarize_deal_context

# Attempt to import CrewAI and LangChain libraries safely
try:
    from crewai import Crew, Agent, Task, Process # Added Process
    from langchain_openai import ChatOpenAI
    CREWAI_SDK_AVAILABLE = True
    logger = logging.getLogger(__name__) # Define logger only if SDK might be used
    logger.debug("CrewAI and LangChain SDKs found.")
except ImportError:
    CREWAI_SDK_AVAILABLE = False
    # Define dummy classes if SDK not installed so the rest of the file can parse
    class Crew: pass
    class Agent: pass
    class Task: pass
    class ChatOpenAI: pass
    class Process: pass # Dummy Process class
    # Setup a dummy logger if SDK is missing, so calls don't fail immediately
    import logging # Need logging even if SDK missing
    logger = logging.getLogger(__name__)
    logger.warning("CrewAI or LangChain SDK not installed (`pip install crewai langchain-openai`). CrewAI operations will be skipped/fail.")


# Initialize LLM only if SDK and Key are available
llm: Optional[ChatOpenAI] = None # Use the imported Optional
if CREWAI_SDK_AVAILABLE and OPENAI_API_KEY:
    try:
        llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=CREWAI_LLM_MODEL,
            temperature=CREWAI_LLM_TEMPERATURE # Use low temp for structured output
            # Consider adding max_retries if needed
            # max_retries=2,
        )
        logger.info(f"✅ CrewAI LLM initialized ({CREWAI_LLM_MODEL}, Temp: {CREWAI_LLM_TEMPERATURE})")
    except Exception as e:
        logger.error(f"❌ Failed to initialize CrewAI LLM: {e}", exc_info=True)
elif CREWAI_SDK_AVAILABLE and not OPENAI_API_KEY: # SDK installed but key missing
     logger.warning("⚠️ OpenAI API Key not found in configuration. CrewAI LLM initialization skipped.")
# No need for else, warning already logged if SDK missing


class TargetAccountCrew:
    """Builds and configures the CrewAI agents and tasks for target account processing."""

    def __init__(self, contact: dict):
        """
        Initializes the crew builder with enriched contact data.

        Args:
            contact: The fully enriched contact dictionary.

        Raises:
            TypeError: If contact is not a dictionary.
        """
        if not isinstance(contact, dict):
             logger.error("Initialization failed: TargetAccountCrew requires a dictionary for contact data.")
             raise TypeError("TargetAccountCrew requires a dictionary for contact data.")
        self.contact = contact
        logger.debug("TargetAccountCrew initialized with contact data.")

    def build(self) -> Tuple[Optional[Crew], List[Task]]:
        """
        Builds the CrewAI crew with agents and tasks.

        Returns:
            A tuple containing:
            - The configured Crew object (or None if LLM/SDK unavailable or setup failed).
            - A list of the defined Task objects (empty list on failure).
        """
        if not llm:
            logger.error("Cannot build CrewAI crew: LLM not initialized.")
            return None, []

        # Prepare context string AND an escaped version for injection
        try:
            contact_context_json = json.dumps(self.contact, indent=2, default=str)
            # --- ADD ESCAPING STEP ---
            escaped_contact_context = contact_context_json.replace('{', '{{').replace('}', '}}')
            # --- END ESCAPING STEP ---
            logger.debug("Prepared and escaped contact data JSON string for Analyst prompt injection.")
        except TypeError as e:
            logger.error(f"❌ Failed to serialize contact data to JSON: {e}", exc_info=True)
            return None, []

        # --- Define Agents ---
        try:
            # Strategist Agent (remains the same)
            strategist = Agent(
                role="B2B Sales Strategist for ABM",
                goal=(
                    "Analyze the provided target contact and company profile (available implicitly). "
                    "Identify 2-3 likely business pains or strategic opportunities based on their industry, size, revenue, role, and company summary. "
                    "Craft a concise (2-4 sentences) and highly relevant outreach angle/hook connecting a generic B2B SaaS solution (focused on growth/efficiency/data insights) to these specific pains/opportunities."
                ),
                backstory=(
                    "You are an expert B2B sales strategist specializing in Account-Based Marketing (ABM). "
                    "You excel at quickly interpreting company and contact data (available implicitly) to formulate compelling, personalized outreach messaging angles "
                    "that resonate deeply with potential buyers' most pressing challenges and strategic goals."
                ),
                verbose=True,
                llm=llm,
                allow_delegation=False
            )
            logger.debug("Sales Strategist agent defined.")

            # Analyst Agent (remains the same)
            analyst = Agent(
                role="Account Data Structuring Analyst",
                goal=(
                    "Extract key contact and firmographic data points accurately from the provided enriched profile data. "
                    "Structure this information precisely into a standardized JSON object format, ensuring all specified fields are included using the exact field names requested."
                ),
                backstory=(
                    "You are a meticulous data analyst focused on data accuracy and adherence to structure. "
                    "Your role is to process enriched account information and prepare clean, reliable data briefs in JSON format. "
                    "You pay extremely close attention to detail, requested field names, and required output formats (JSON only)."
                ),
                verbose=True,
                llm=llm,
                allow_delegation=False
            )
            logger.debug("Account Data Analyst agent defined.")

        except Exception as e:
             logger.error(f"❌ Failed to define CrewAI agents: {e}", exc_info=True)
             return None, []


        # --- Define Tasks ---
        analyst_fields_list = ['name', 'email', 'title', 'phone', 'company', 'domain', 'revenue', 'employees', 'linkedin', 'linkedin_company_page', 'summary']
        analyst_fields_str = ", ".join([f"'{f}'" for f in analyst_fields_list]) # For use in prompts

        tasks_list = []
        try:
            # Strategist Task (No change needed here as it doesn't inject JSON)
            task1_strategize = Task(
                description=(
                    f"**Task: Develop Outreach Angle**\n\n"
                    f"Context: Detailed profile for contact '{self.contact.get('name', 'N/A')}' at company '{self.contact.get('company', 'N/A')}' is provided implicitly through the crew's input.\n\n"
                    f"Instructions:\n"
                    f"1. Carefully analyze the complete profile data available implicitly in the context.\n"
                    f"2. Identify 2-3 specific, potential business challenges OR strategic opportunities relevant to this company, considering their summary, industry (implied), revenue ({self.contact.get('revenue', 'N/A')}), and employee count ({self.contact.get('employees', 'N/A')}).\n"
                    f"3. Synthesize these insights into a concise (strictly 2-4 sentences) outreach angle. This angle should briefly mention the challenge/opportunity and hint at how a generic B2B SaaS solution could help.\n"
                    f"4. Output *only* the angle text itself, nothing else."
                ),
                agent=strategist,
                expected_output="A short paragraph (2-4 sentences maximum) containing only the tailored outreach angle text.",
            )
            tasks_list.append(task1_strategize)
            logger.debug("Strategist task defined.")

            # Analyst Task - Use the *escaped* JSON string in the description
            task2_structure_data = Task(
                description=(
                    f"**Task: Extract and Structure Specific Account Data as JSON**\n\n"
                    f"**Source Data:** You MUST use ONLY the following JSON data as your source:\n"
                    f"```json\n"
                    # --- USE ESCAPED STRING ---
                    f"{escaped_contact_context}\n"
                    # --- END CHANGE ---
                    f"```\n\n"
                    f"**Instructions:**\n"
                    f"1. **CRITICAL:** Ignore any other context, thoughts, or outputs from previous tasks/agents. Focus ONLY on the 'Source Data' JSON provided above.\n"
                    f"2. From the 'Source Data' JSON, extract the exact values for these specific fields: {analyst_fields_str}.\n"
                    f"3. Use the field names in the context JSON (e.g., 'name', 'email', 'revenue', etc.) to find the corresponding values.\n"
                    f"4. If a field listed in instruction 2 is missing from the 'Source Data' JSON, or its value is null/empty string, use the JSON value `null` (not the string \"null\") for that key in your output JSON.\n"
                    f"5. Construct a single, valid JSON object containing these key-value pairs using the exact field names ({analyst_fields_str}) as the keys.\n"
                    f"6. **CRITICAL:** Your final output MUST be ONLY the raw JSON object string. Do NOT include ```json markdown, explanations, or any surrounding text."
                ),
                agent=analyst,
                # Simplified expected_output - focuses on format, not content example
                expected_output=(
                    f"A single, valid, raw JSON object string containing key-value pairs ONLY for the fields: {analyst_fields_str}. "
                    f"Values must be extracted solely from the Source Data provided in the task description."
                ),
            )
            tasks_list.append(task2_structure_data)
            logger.debug("Analyst task defined with escaped injected context.")

        except Exception as e:
             logger.error(f"❌ Failed to define CrewAI tasks: {e}", exc_info=True)
             return None, []


        # --- Create and Configure Crew ---
        try:
            # Context is usually passed to crew.kickoff(), not the Crew constructor itself
            account_crew = Crew(
                agents=[strategist, analyst],
                tasks=tasks_list,
                process=Process.sequential,
                verbose=True
                # memory=True # Enable memory=True if you explicitly need the Analyst to see Strategist output
            )
            logger.info("✅ CrewAI Crew configured successfully (Sequential Process).")
            return account_crew, tasks_list

        except Exception as e:
            logger.error(f"❌ Failed to create CrewAI Crew object: {e}", exc_info=True)
            return None, []