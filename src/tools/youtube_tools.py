from langchain_core.tools import tool
from crewai import Task, Crew, Process, Agent
from crewai_tools import YoutubeChannelSearchTool


@tool
def Youtube_BlogPost(channel: str, topic: str) -> str:
    """Search YouTube channel and write a blog post based on the topic"""
    yt_tool = YoutubeChannelSearchTool(youtube_channel_handle=f"@{channel}")

    # Researcher Agent
    blog_researcher = Agent(
        role = "Blog Researcher",
        goal = "Get the relevant video content for the topic {topic} from the YT channel",
        verbose = True,
        memory = True,
        backstory = (
            "You are an expert in understanding videos in the AI Data Science, ML and Gen AI space."
        ),
        tools = [yt_tool],
        allow_delegation = True
    )

    # Content Writer Agent
    blog_writer = Agent(
        role = "Blog Writer",
        goal = "Narrate compelling stories about the video {topic} from YT channel",
        verbose = True,
        memory = True,
        backstory = (
            """
            You are expert in simplifying complex topics and craft engagin narratives that captivate and educate.
            """
        ),
        tools = [yt_tool],
        allow_delegation = False
    )

    research_task = Task(
        description = (
            "Identify the video {topic}."
            "Get detailed information about the video from the channel."
        ),
        expected_output = "A comprehensive 3 paragraphs long report based on the {topic} of the video.",
        tools = [yt_tool],
        agent = blog_researcher
    )

    write_task = Task(
        description = (
            "Get detailed information from the youtube channel on the topic {topic}."
        ),
        expected_output = "Summarize the info from the youtube channel video on the topic {topic} and create the content for the blog.",
        tools = [yt_tool],
        agent = blog_writer,
        async_execution = False,
        output_file = 'blog_post.md'
    )

    crew = Crew(
        agents = [blog_researcher, blog_writer],
        tasks = [research_task, write_task],
        process = Process.sequential,
        memory = True,
        cache = True,
        max_rpm = 100,
        share_crew = True
    )

    output = crew.kickoff(inputs = {'topic': topic})

    return output.raw