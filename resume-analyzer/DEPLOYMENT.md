# Deployment Guide - HireFlow Resume Analyzer

## Overview

This guide provides step-by-step instructions for deploying the HireFlow Resume Analyzer to Vercel's free tier.

## Prerequisites

- GitHub account (free)
- Vercel account (free)
- Node.js 18+ installed locally
- Git installed locally

## Step 1: Prepare Your Repository

### 1.1 Initialize Git (if not already done)

```bash
cd resume-analyzer
git init
```

### 1.2 Create .gitignore

The `.gitignore` file is already included in the project. It excludes:
- `node_modules/`
- `.next/`
- `.env.local`
- Build artifacts

### 1.3 Commit Your Code

```bash
git add .
git commit -m "Initial commit: HireFlow Resume Analyzer"
```

## Step 2: Create GitHub Repository

### 2.1 Create New Repository

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `hireflow-resume-analyzer`
3. Description: `AI-powered resume analysis tool for Digital Heroes Developer Trial`
4. Make it **Public** (required for Vercel free tier)
5. Don't initialize with README (we already have one)
6. Click "Create repository"

### 2.2 Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/hireflow-resume-analyzer.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## Step 3: Deploy to Vercel

### 3.1 Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up"
3. Sign up with GitHub (recommended)
4. Verify your email

### 3.2 Import Your Repository

1. Click "Add New..." → "Project"
2. Vercel will show your GitHub repositories
3. Find and click `hireflow-resume-analyzer`
4. Click "Import"

### 3.3 Configure Project

Vercel will automatically detect Next.js and configure:

**Framework Preset**: Next.js
**Root Directory**: `./`
**Build Command**: `npm run build`
**Output Directory**: `.next` (or `out` for static export)

**Environment Variables**:
- No environment variables required for the demo version

### 3.4 Deploy

1. Click "Deploy"
2. Wait for deployment to complete (usually 1-2 minutes)
3. Vercel will provide a URL like: `https://hireflow-resume-analyzer.vercel.app`

## Step 4: Verify Deployment

### 4.1 Test the Live Site

1. Open the provided Vercel URL
2. Verify the homepage loads correctly
3. Test the resume upload feature
4. Check that the analysis works
5. Verify the "Built for Digital Heroes" button links correctly
6. Check that your name and email appear in the footer

### 4.2 Check All Requirements

✅ Tool works and gives correct output
✅ Button labeled "Built for Digital Heroes" links to https://digitalheroesco.com
✅ Your full name and email are visible in the footer
✅ Live and deployed on Vercel free tier
✅ Public GitHub repository
✅ ₹0 spent (no paid subscriptions)

## Step 5: Custom Domain (Optional)

### 5.1 Add Custom Domain

1. Go to your Vercel project dashboard
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Follow DNS configuration instructions

### 5.2 Update DNS

1. Go to your domain registrar
2. Add CNAME record pointing to `cname.vercel-dns.com`
3. Wait for DNS propagation (usually 5-10 minutes)

## Step 6: Monitor and Maintain

### 6.1 View Deployment Logs

1. Go to Vercel project dashboard
2. Click "Deployments"
3. Click on a deployment to view logs

### 6.2 Set Up Alerts (Optional)

1. Go to Vercel project dashboard
2. Click "Settings" → "Notifications"
3. Configure email alerts for deployments and errors

### 6.3 Update Deployment

To update the application:

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main

# Vercel auto-deploys on push to main
```

## Troubleshooting

### Build Fails

**Issue**: Build fails during deployment

**Solutions**:
- Check build logs in Vercel dashboard
- Ensure `package.json` is correct
- Verify all dependencies are listed
- Try building locally first: `npm run build`

### Deployment Fails

**Issue**: Deployment fails after build succeeds

**Solutions**:
- Check deployment logs in Vercel dashboard
- Ensure `next.config.js` is correct
- Verify `output: 'export'` is set for static export
- Check for missing environment variables

### 404 Errors

**Issue**: Pages return 404 errors

**Solutions**:
- Ensure `next.config.js` has `output: 'export'`
- Check that all pages are in `src/app/` directory
- Verify file names are correct

### Button Link Not Working

**Issue**: "Built for Digital Heroes" button doesn't link correctly

**Solutions**:
- Check that the link in `src/app/page.tsx` is correct
- Verify the link in `src/components/ResumeAnalyzer.tsx` is correct
- Ensure the URL is `https://digitalheroesco.com`

### Name/Email Not Showing

**Issue**: Name and email not visible in footer

**Solutions**:
- Check footer component in both page files
- Verify the text is correct
- Ensure CSS is not hiding the footer

## Cost Verification

### Vercel Free Tier Limits

- **Hobby Plan**: $0/month
- **Bandwidth**: 100 GB/month
- **Build Minutes**: 6,000/month
- **Serverless Function Execution**: 100 GB-hours/month

### Verify No Costs Incurred

1. Go to Vercel dashboard
2. Click "Settings" → "Billing"
3. Verify you're on the Hobby plan
4. Check that no charges have been incurred

## Security Best Practices

### 1. Never Commit Secrets

- Never commit `.env.local` files
- Never commit API keys
- Use Vercel environment variables for secrets

### 2. Use HTTPS

- Vercel automatically provides HTTPS
- No additional configuration needed

### 3. Set Up CSP Headers (Optional)

Add to `next.config.js`:

```javascript
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
          },
        ],
      },
    ];
  },
};
```

## Performance Optimization

### 1. Enable Caching

Vercel automatically caches static assets. No additional configuration needed.

### 2. Optimize Images

The application uses SVG icons (Lucide React) which are already optimized.

### 3. Minimize JavaScript

Next.js automatically minifies JavaScript during build.

## Analytics (Optional)

### Vercel Analytics

1. Go to Vercel project dashboard
2. Click "Analytics"
3. Enable Vercel Analytics (free)
4. Add the analytics package:

```bash
npm install @vercel/analytics
```

5. Add to `src/app/layout.tsx`:

```typescript
import { Analytics } from '@vercel/analytics/react';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

## Backup Strategy

### Automatic Backups

Vercel automatically keeps:
- Latest deployment
- Previous deployments (up to 25 on free tier)

### Manual Backup

To backup your code:

```bash
# Create a backup branch
git branch backup
git push origin backup
```

## Rollback

If deployment fails:

1. Go to Vercel project dashboard
2. Click "Deployments"
3. Find the previous successful deployment
4. Click "..." → "Promote to Production"

## Next Steps

After successful deployment:

1. ✅ Test all features
2. ✅ Verify all Digital Heroes requirements
3. ✅ Share the live URL
4. ✅ Add to your portfolio
5. ✅ Prepare Digital Heroes submission

## Support

If you encounter issues:

- Check Vercel deployment logs
- Review this guide
- Check Next.js documentation
- Open an issue on GitHub

---

**Deployment Status**: Ready for Vercel  
**Platform**: Vercel (Free Tier)  
**Cost**: $0/month  
**Last Updated**: June 20, 2026
