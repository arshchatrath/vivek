import type { Metadata } from "next";
import GeneralChat from "../general-chat";
import "../general.css";

export const metadata: Metadata = {
  title: "General wellness chat | Vivek",
  description: "Use Groq to ask about general wellness, ingredients, and Mosaic Wellness product listings.",
};

export default function GeneralChatPage() {
  return <GeneralChat />;
}
