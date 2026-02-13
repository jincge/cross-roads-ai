


Please choose!   Copyright © 2026  Capgemini. All rights reserved.  3
1 Introduction  
Focusing on Gen -AI Integration in Software Development  and Test Engineering  
This individual programming exercise is designed primarily to give engineers a hands -on opportunity to
learn and practice using generative AI (gen -ai) tools in the context of software development  and test
automation . The assigned project —a simulation and visualization of traffic lights at a busy crossroad —
serves mainly as a means to facilitate practical gen -ai exploration rather than to deeply study traffic
control systems.  
Participants will create a software application that models and visually represents traffic light changes. The
main objective is to integrate gen -ai throughout the workflow: for assistance with designing algorithms,
optimizing code, generating documentatio n, or producing visual assets. The scenario provides a concrete
base for engineers to experiment with and benefit from AI -driven tools during real development tasks.  
Deliverables should include a working simulation, a visualization of traffic light states, and a short
reflection on the use and impact of gen -ai throughout the project. The ultimate goal is to build confidence
and familiarity with AI integration in day -to-day programming  and test development .
--- page 4 ---

Please choose!   Copyright © 2026  Capgemini. All rights reserved.  4
2 Integrating Generative AI with GitHub Copilot  
2.1 Introduction to Gen -AI and GitHub Copilot in VSCode  
Generative AI (Gen -AI) is reshaping software engineering by automating code generation, explanation, and
review tasks. GitHub Copilot, a prominent Gen -AI tool, integrates directly with Visual Studio Code (VSCode)
to augment developer productivity and strea mline workflows. By leveraging Copilot, engineers can
generate code snippets, resolve issues, and maintain documentation more efficiently, making it a valuable
asset in modern software development environments.  
This chapter provides a technical, step -by-step guide for software engineers on using GitHub Copilot in
VSCode, covering environment setup, code generation, debugging, testing, and documentation practices.  
The goal is to equip developers with practical techniques for integrating Gen -AI into their day -to-day
programming.  
The following sections are so organized:  
a. Setup and configuration of the working environment  
b. Enhance  your  working environment  
c. Application development , debugging and testing  
d. Enhance continuous integration workflow  
e. Refactoring, Reviewing and Documentation

Every section and/or subsection is annotated with a difficulty level:  
• Beginner : expected by everyone without a specific role  
• Intermediate : from developer to lead engineer  
• Advance: from lead engineer to architect  
Setup and configuration of the working environment  
2.1.1  Create a repository in a versioning system    
GitHub is a cloud ‑based platform for hosting Git repositories that enables developers to store, manage,
and collaborate on code using tools like pull requests, issue tracking, and project management . Having the
project in one of such  system s, is today a defector standard for project maintainability.  Here are the
directives to create a repository on github.
1. How to c reate a new repository :
   o Click on New  (usually found in the top -right corner or under your profile menu).  
   o Fill in the details: Repository Name , Description  (optional) , and Visibility  
   o Initialize with README : Check this option to have  a README file created automatically.  
   o Add a .gitignore file to exclude unnecessary files
2. How to locally clone a repository  
   o Copy the repository URL (HTTPS or SSH).  
   o Run the following command in your terminal:  git clone <repository -url>  
   --- page 5 ---

Please choose!   Copyright © 2026  Capgemini. All rights reserved.  5
2.1.2  Setting Up  VS Code  Working Environment   
An IDE (Integrated Development Environment) is a software application that provides developers with a
complete set of tools —like a code editor, debugger, and build system —all in one place to make writing and
managing code easier and more efficient.  Here are the directives to  install VS code and Copilot extension:
1. Install Visual Studio Code:  Download and install the latest version of VSCode from the official
   website. Ensure your system meets the recommended requirements for optimal performance.
2. Install GitHub Copilot Extension:  Open VSCode, go to the Extensions view (Ctrl+Shift+X), search
   for "GitHub Copilot," and click "Install." Sign in with your GitHub account to activate Copilot.  
   2.2 Enhance  your  working environment  
   2.2.1  Customize VS code workflow s  
   To streamline and automate your entire development workflow, VS Code lets you customize how your
   application should be  built, run, and debugged.  To maximize its support to your needs:
1. Configuring Compile, Debug, and Run workflow  in VSCode : you can use tasks.json  file to define
   custom build and run workflow , and the launch.json  file for debugging configurations. Copilot can
   provide suggestions for these configuration files based on your project's language and structure.
   Once set up, Vs Code UI allows you to quickly build, debug, and run your application with a single
   click.  
   2.2.2  Make  Cop ilot’s answers meet your expectations   
   GitHub Copilot can accelerate development by generating code based on natural language comments or
   partial code snippets. However, without some context and guidelines you will keep iterating with it about
   the same concept s and workflows repeatedly. To maximize its effectiveness:
1. Define user prompt files  for Copilot : Write prompts file to define reusable prompts for common
   development tasks such as  generating  git branches, source code, performing code reviews , and any
   task -specific guidelines or reference  architecture instructions to ensure consistent execution  and
   code quality.  Copilot can help you with suggestions for these prompt files. Additionally, you take
   inspira tion from the repository https://github.com/github/awesome -copilot
2. Define user instruction file s for Copilot:  Instead of manually including context and examples in
   every chat prompt , write instruction files to  define common guidelines and rules that automatically
   influence how AI generates source code , documentation  and handles other development tasks  for
   you. Copilot can help you with suggestions for these prompt files. Additionally, you take inspiration
   from the repository https://github.com/github/awesome -copilot  
   2.3 Application development, debugging and  unit  testing  
   Before continuing, recall that you cannot expect correct -by-generation code . Copilot is used to speed up
   coding related tasks and brainstorming where solutions are evaluated. When any solution is provided, you
   remain the final evaluator and expert, with Copilot supporting you as a colleague at your side.  
   2.3.1  Generate code with Copilot   
   Do not write code but  ask Copilot to generat e code based on a natural language description and  use cases .  
   --- page 6 ---

Please choose!   Copyright © 2026  Capgemini. All rights reserved.  6
1. Ask Copilot to generate your  application by proving a clear, intent -driven description of  the desired
   functionalit ies. Include examples in the description to narrow the  answer and decrease the number
   of interactions with agent.
2. Review Copilot’s suggestions and select, edit, or reject them as appropriate for your use case.
3. Use Copilot for boilerplate code, repetitive patterns, or complex algorithm scaffolding, ensuring
   you maintain control over logic and security.  
   NOTE:  
   user  instructions can improve the quality of the generated  source code tremendously based on quality
   standards, expected error -handling logics, documentation and many other  code -related  aspects  
   (Chapter 1.3 ).
4. Application -Specific Libraries:  Use package managers (like npm, pip,  conan, or nuget) to install
   required libraries. Copilot can assist by suggesting dependency lists in manifest files (e.g.,
   package.json, requirements.txt).  
   2.3.2  Debugging code and resolving issues   
   Recall: Generative AI does not mean  correct by generation  solution . Depending on internal rules, context
   and your description you have the most likely answer. Thus, the execution of corner case s, and detection of
   unwanted behavior  remains a human task.
1. Identifying Errors:  When you encounter warnings or runtime errors, Copilot can suggest  fixes.
   Place your cursor near the problematic code or describe the issue in a comment to prompt Copilot
   for suggestions.  Additionally, you can report the actual behavior  (such as a wrong output value)
   and remark Copilot the one you expected to have .
2. Resolving Warnings:  Copilot can suggest code modifications to resolve common warnings, such as
   type mismatches, deprecated API usage, or uninitialized variables.
3. Debugging Techniques:  Use VSCode’s built -in debugger in conjunction with Copilot for step -by-
   step troubleshooting. Copilot can help generate logging statements or identify likely sources of
   bugs.  
   2.3.3  Unit t esting   
   A good regression test is  essential as it helps ensure software quality, stability, and long -term
   maintainability throughout the development process  of the application.

1. Create unit and integration Tests:  Write comments specifying the function to test and the
   expected behavior. You can ask Copilot to generate  unit and component test templates using
   popular frameworks (e.g., pytest, Jest, xUnit , catch2, gtest ). Do not stop on the “happy path” but
   ask to cover corner cases .
2. Create Functional Tests:  Write comments specifying the function ality  to test and the expected
   behavior  at application level to ensure user -test cases are covered. Copilot can help you generate
   complex test scenarios mimicking users’  interactions.  
   2.3.4  Test coverage   
   A good regression test is thought to be “good ” when no cover case is left out. Test coverage is a technic to
   evaluate  the “goodness” of your regression test.
3. Generate Test Coverage:  With Copilot, you can define  a workflow for your regression  tests where
   test coverage metadata  is generated to show in a user readable means  what code is tested and  
   untested.  
   --- page 7 ---

Please choose!   Copyright © 2026  Capgemini. All rights reserved.  7
4. Optimizing Test Coverage:  Review the generated coverage report and ask Copilot  to generate
   test scenario to cover uncovered execution paths.  
   2.4 Module and System Testing   
   Where unit testing and integration  testing is in the domain of software development, module and system
   testing is in the domain of test engineering.
1. Requirements Analysis:  Leverage AI -powered tools to parse specifications, analyze requirements
   documents, and extract or even generate testable requirements. These tools can flag ambiguities
   and suggest clarifications, ensuring the foundation for testing is robust and clear.
2. Test Plan Creation:  Use AI assistants to help draft comprehensive test plans. They can propose
   test objectives, scope, resource estimates, and schedules based on project context, past plans, and
   best practices, accelerating the planning phase and reducing omissions.
3. Tool Selection:  For the selection of tools to be used, you have to consider the test framework, the
   availability of libra ries, the technology to  access the application under test , and the programming
   language (s) to realize  the missing pieces. AI agen ts can assist you with an overview of available
   options and the suitability of these options for the pro blem at hand.
4. Test Case Creation:  AI tools can auto -generate detailed test cases from requirements or user
   stories, covering both typical flows and edge cases. They also help maintain and update test cases
   as the system evolves, ensuring ongoing relevance and high coverage.
5. Keyword Development:  Modern AI assistants can suggest, refactor, or optimize test automation
   keywords and reusable actions, enhancing maintainability and supporting efficient expansion of
   automated test suites.
6. Reporting:  In the end, we want to showcase the results of our efforts using nice looking repo rts.  
   2.5 Enhance c ontinuous integration  workflow   
   Continuous integration is crucial for maintaining quality throughout a project’s development and for
   promptly raising alerts when standards are not met  or current implementation can be broken by new code .
1. Create pipelines for GitLab : with Copilot you can  generate pipelines that run regression tests,
   send email alerts, and block new code  when errors occur.
2. Schedule periodic checks:  you can  generate pipelines periodically executed by GitLab  to check  
   code coverage and raise aler ts if code/test quality  falls below the required threshold.
3. Create manual or tag -based actions : with Copilot you can generate action for GitLab , for instance
   generate  an installable package whenever a tag is added to a Git commit.  
   2.6 Refactoring , review and documentation  
   Effective development relies on improving code quality, understanding existing logic, and maintaining
   clear documentation —practices that support long ‑term project health with Copilot as a helpful partner
   throughout.    
   --- page 8 ---

Please choose!   Copyright © 2026  Capgemini. All rights reserved.  8
2.6.1  Refactoring Code
1. Improving Structure:  Copilot can be used to  suggest refactoring options, such as extracting
   methods, renaming variables, or simplifying complex statements.
2. Enhancing Readability:  Ask Copilot to rewrite sections for clarification or to conform  code  to
   coding standards. Review and test all refactored code to ensure functionality is preserved !
3. Explore alternatives:  Use Copilot to suggest alternative implementations or highlight potential
   issues, but always conduct a thorough manual review for logic, security, and maintainability.   
   2.6.2  Reviewing  
   Code review is essential for quality assurance .
1. Check for uninitialized variables and race condition : Ask Copilot  to analyze the new code and
   identify any critical aspect.
2. Check for coding conventions : Ask Copilot to analyze the new code and identify any missed code
   convention and /or violation  compared to  your reference architecture.
3. Clarify logic and intent  by writing a comment like #Explain this function above a code block,
   Copilot can generate summaries or inline comments to clarify logic and intent. Always review these
   explanations for technical accuracy and completeness before sharing with others.  
   2.6.3  Documentation  and explaining c ode  
   Documentation tends to diverge from source code when it is not updated and maintained. Y ou can use
   Copilot to update and check if source code follows the intent  describe d.
1. Generate summaries  of code  by prompting Copilot with comments like #Summarize this
   function’s changes.
2. Generating Documentation:  Leverage Copilot to create or update README.md files, API docs, and
   inline comments. Prompt detailed descriptions to receive relevant sections or summaries.
3. Create user prompt file  to a utomatically detect technology stacks and architectural patterns,
   generate  visual diagrams, documents implementation patterns, and provides extensible blueprints
   for maintaining architectural consistency and guiding new development.  
   2.7 Conclusion  
   Integrating GitHub Copilot with VSCode empowers software engineers to automate repetitive tasks,
   enhance productivity, and maintain high code quality. By following these technical guidelines, developers
   can effectively leverage Gen -AI throughout the softwa re development lifecycle —from initial setup and
   code generation to testing, explanation, and documentation. Continuous practice with Copilot will deepen
   familiarity with AI -driven workflows and support ongoing professional growth in an evolving field.  
   