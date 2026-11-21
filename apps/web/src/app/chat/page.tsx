import type { Metadata } from "next";
import Conversation from "./conversation";
import "./conversation.css";

export const metadata: Metadata = {
  title: "Ask Vivek | Wellness chat",
  description: "Ask about a wellness concern and read guidance with links to the original sources.",
};

export default function ChatPage() {
  return <Conversation />;
}
