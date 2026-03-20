import ToolJobList from "@/components/ToolJobList";

export default function LlmsTxtPage() {
  return (
    <ToolJobList 
      toolName="LLMS.txt Generator" 
      toolPath="llms-txt"
      description="Generate an LLM-friendly documentation file for your website to improve how AI agents understand and summarize your content."
    />
  );
}
