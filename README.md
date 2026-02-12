# AI/LLM Portfolio Website

A modern, minimal portfolio website showcasing AI and Large Language Model (LLM) projects. Built with Next.js 14, React, TypeScript, and Tailwind CSS.

## Features

- 🎨 Clean, minimal design with Tailwind CSS
- 📱 Fully responsive layout (mobile, tablet, desktop)
- ⚡ Fast performance with Next.js App Router
- 🔍 SEO-optimized with proper metadata
- 🎯 Smooth scrolling navigation
- 💼 Showcase 6 placeholder AI/LLM projects
- 🔗 Social links and contact section
- 📦 TypeScript for type safety

## Project Structure

```
ai-llm-portfolio/
├── src/
│   ├── app/
│   │   ├── layout.tsx        # Root layout with metadata
│   │   ├── page.tsx          # Home page
│   │   └── globals.css       # Global styles + Tailwind
│   ├── components/
│   │   ├── Hero.tsx          # Hero section
│   │   ├── Navbar.tsx        # Navigation bar
│   │   ├── ProjectCard.tsx   # Project card component
│   │   ├── ProjectsGrid.tsx  # Projects grid container
│   │   └── Footer.tsx        # Footer with social links
│   ├── data/
│   │   └── projects.ts       # Project data (easily editable)
│   └── types/
│       └── project.ts        # TypeScript types
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.ts
```

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- npm, yarn, or pnpm

### Installation

1. Clone the repository:
```bash
cd /Users/omi/Documents/ai-llm-portfolio
```

2. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

3. Run the development server:
```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Customization

### Update Projects

Edit `src/data/projects.ts` to add or modify your projects:

```typescript
{
  id: 'unique-id',
  title: 'Your Project Name',
  description: 'Project description...',
  techStack: ['Tech1', 'Tech2', 'Tech3'],
  githubUrl: 'https://github.com/yourusername/repo',
  demoUrl: 'https://demo.example.com', // optional
}
```

### Update Personal Information

1. **Hero Section**: Edit `src/components/Hero.tsx`
   - Change name, title, and bio text

2. **Navigation**: Edit `src/components/Navbar.tsx`
   - Update logo/brand name

3. **Social Links**: Edit `src/components/Footer.tsx`
   - Replace placeholder URLs with your actual social media links

4. **Metadata**: Edit `src/app/layout.tsx`
   - Update title, description, and keywords for SEO

### Customize Colors

Tailwind colors are defined in `tailwind.config.ts`. The default accent color is blue. To change:

```typescript
theme: {
  extend: {
    colors: {
      primary: '#your-color',
    },
  },
}
```

Then replace `blue-600`, `blue-700`, etc. with `primary` in components.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Font**: Inter (Google Fonts)
- **Icons**: Heroicons & Custom SVG

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import your repository on [Vercel](https://vercel.com)
3. Deploy with zero configuration

### Other Platforms

This is a standard Next.js app and can be deployed to:
- Netlify
- AWS Amplify
- Railway
- Render
- Your own server with Node.js

## License

MIT License - feel free to use this template for your own portfolio!

## Future Enhancements

- [ ] Dark mode toggle
- [ ] Blog section
- [ ] Contact form with backend
- [ ] Project filtering
- [ ] Animations
- [ ] Case study pages for each project

---

Built with ❤️ using [Next.js](https://nextjs.org)
