import { Project } from '@/types/project'

export const projects: Project[] = [
  {
    id: 'code-docgen',
    title: 'AI Code Documentation Generator',
    description: 'Fine-tuned CodeLlama-7B using QLoRA to automatically generate Python docstrings with 78% improvement over base model (BLEU: 0.23→0.41). Trained on 8K examples in 3 hours on free Colab GPU with interactive demo showing side-by-side comparisons.',
    techStack: ['PyTorch', 'HuggingFace', 'QLoRA', 'CodeLlama-7B', 'Gradio', 'Transformers'],
    githubUrl: 'https://github.com/bilbobaggins90/ai-code-docgen',
    demoUrl: 'https://huggingface.co/spaces/YOUR_USERNAME/code-docgen',
  },
  {
    id: 'gpt-chatbot',
    title: 'GPT-based Chatbot',
    description: 'An intelligent conversational AI powered by GPT-4 with context awareness and multi-turn dialogue capabilities. Features custom prompt engineering and conversation memory.',
    techStack: ['OpenAI API', 'Python', 'LangChain', 'FastAPI', 'React'],
    githubUrl: 'https://github.com/yourusername/gpt-chatbot',
    demoUrl: 'https://demo.example.com',
  },
  {
    id: 'document-qa',
    title: 'LangChain Document Q&A System',
    description: 'Document question-answering system using LangChain for semantic search and retrieval. Supports multiple document formats with advanced chunking strategies.',
    techStack: ['LangChain', 'OpenAI', 'ChromaDB', 'Python', 'Streamlit'],
    githubUrl: 'https://github.com/yourusername/document-qa',
  },
  {
    id: 'classification-model',
    title: 'Fine-tuned Classification Model',
    description: 'Custom fine-tuned BERT model for domain-specific text classification with 95%+ accuracy. Includes data preprocessing pipeline and model evaluation suite.',
    techStack: ['PyTorch', 'Transformers', 'BERT', 'Python', 'scikit-learn'],
    githubUrl: 'https://github.com/yourusername/classification-model',
  },
  {
    id: 'rag-pipeline',
    title: 'RAG Pipeline',
    description: 'Production-ready Retrieval Augmented Generation system with hybrid search, re-ranking, and citation tracking. Built for enterprise-scale knowledge bases.',
    techStack: ['LangChain', 'Pinecone', 'GPT-4', 'Python', 'Docker'],
    githubUrl: 'https://github.com/yourusername/rag-pipeline',
    demoUrl: 'https://rag-demo.example.com',
  },
  {
    id: 'prompt-toolkit',
    title: 'Prompt Engineering Toolkit',
    description: 'Comprehensive toolkit for prompt engineering with template management, version control, and A/B testing capabilities. Includes prompt optimization algorithms.',
    techStack: ['Python', 'OpenAI', 'Anthropic Claude', 'React', 'TypeScript'],
    githubUrl: 'https://github.com/yourusername/prompt-toolkit',
  },
  {
    id: 'content-generator',
    title: 'AI Content Generator',
    description: 'Multi-modal AI content generation platform supporting text, code, and structured data. Features style transfer and tone adjustment with custom fine-tuning.',
    techStack: ['GPT-4', 'Python', 'Next.js', 'PostgreSQL', 'Tailwind CSS'],
    githubUrl: 'https://github.com/yourusername/content-generator',
    demoUrl: 'https://content-gen.example.com',
  },
]
