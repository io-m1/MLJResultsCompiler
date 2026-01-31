# MLJ Results Compiler - Render.com Deployment Configuration

# Configuration for deploying Node.js backend to Render.com
# Follow these steps to deploy:

## 1. Create Render.com Account
   - Go to render.com
   - Sign up with GitHub account
   - Grant access to your GitHub repository

## 2. Create Web Service
   - Dashboard → New → Web Service
   - Connect your GitHub repo
   - Select the repository

## 3. Configure Service
   Build Command:       npm install
   Start Command:       npm start
   Instance Type:       Starter (free)
   Environment:         Node

## 4. Set Environment Variables
   Click "Add Environment Variable" and set:

   KEY                          VALUE
   ──────────────────────────   ──────────────────────────────
   NODE_ENV                     production
   PORT                         3000
   CORS_ORIGIN                  https://mljresultscompiler.vercel.app
   MAX_FILE_SIZE                10485760
   UPLOAD_DIR                   ./uploads

## 5. Deploy
   - Click "Create Web Service"
   - Render will automatically deploy
   - Get your backend URL (e.g., https://mlj-backend.render.com)

## 6. Update Frontend
   In Vercel frontend settings, add environment variable:
   
   NEXT_PUBLIC_BACKEND_URL=https://mlj-backend.render.com

## 7. Test
   - Visit https://mljresultscompiler.vercel.app/
   - Try uploading files
   - Verify processing works

## Troubleshooting

If backend is not responding:
1. Check Render dashboard for errors
2. View logs: Render → Logs tab
3. Verify environment variables are set
4. Check CORS_ORIGIN matches frontend URL

If uploads fail:
1. Check file size (max 10MB)
2. Verify Excel format (.xlsx)
3. Check backend logs for validation errors

Free tier limitations:
- Spins down after 15 minutes of inactivity
- First request after spin-down takes 30 seconds
- To avoid this, upgrade to Starter plan ($7/month)

## Production Checklist
- [ ] Backend deployed to Render.com
- [ ] Frontend environment variable set
- [ ] CORS configured correctly
- [ ] Test file upload working
- [ ] Test file processing working
- [ ] Test file download working
- [ ] Check logs for errors
- [ ] Monitor performance
