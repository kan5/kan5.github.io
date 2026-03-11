// Portfolio loader — builds grid from manifest.json, handles accordion/lightbox/markdown
(function() {
  'use strict';

  // Reuse lang from index.html global scope, fallback to detection
  const lang = window._portfolioLang || (function() {
    const r = (navigator.language || 'ru').toLowerCase();
    if (r.startsWith('zh')) return 'zh';
    if (r.startsWith('en')) return 'en';
    return 'ru';
  })();

  const portfolioEl = document.getElementById('portfolio');
  if (!portfolioEl) return;

  // Lightbox with gallery navigation
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = lightbox ? lightbox.querySelector('img') : null;
  const lbPrev = lightbox ? lightbox.querySelector('.lb-prev') : null;
  const lbNext = lightbox ? lightbox.querySelector('.lb-next') : null;
  var gallery = [];    // current gallery image URLs
  var galleryIdx = 0;  // current index in gallery

  function closeLightbox() {
    if (lightbox) lightbox.classList.remove('active');
  }

  function showGalleryImage(idx) {
    if (!lightboxImg || gallery.length === 0) return;
    galleryIdx = (idx + gallery.length) % gallery.length;
    lightboxImg.src = gallery[galleryIdx];
    // Show/hide arrows based on gallery size
    if (lbPrev) lbPrev.style.display = gallery.length > 1 ? '' : 'none';
    if (lbNext) lbNext.style.display = gallery.length > 1 ? '' : 'none';
  }

  if (lightbox) {
    // Close on background click (not on image or arrows)
    lightbox.addEventListener('click', function(e) {
      if (e.target === lightbox) closeLightbox();
    });
    if (lbPrev) lbPrev.addEventListener('click', function(e) {
      e.stopPropagation();
      showGalleryImage(galleryIdx - 1);
    });
    if (lbNext) lbNext.addEventListener('click', function(e) {
      e.stopPropagation();
      showGalleryImage(galleryIdx + 1);
    });
    if (lightboxImg) lightboxImg.addEventListener('click', function(e) {
      e.stopPropagation();
    });
    document.addEventListener('keydown', function(e) {
      if (!lightbox.classList.contains('active')) return;
      if (e.key === 'Escape') closeLightbox();
      else if (e.key === 'ArrowLeft') showGalleryImage(galleryIdx - 1);
      else if (e.key === 'ArrowRight') showGalleryImage(galleryIdx + 1);
    });
  }

  function openLightbox(src, images) {
    if (!lightbox || !lightboxImg) return;
    gallery = images || [src];
    galleryIdx = gallery.indexOf(src);
    if (galleryIdx < 0) galleryIdx = 0;
    showGalleryImage(galleryIdx);
    lightbox.classList.add('active');
  }

  // Localized title helper
  function t(obj) {
    if (!obj) return '';
    return obj[lang] || obj.en || obj.ru || '';
  }

  // File type helpers
  function isImage(f) { return /\.(jpg|jpeg|png|gif|webp)$/i.test(f); }
  function isVideo(f) { return /\.(mp4|webm|mov)$/i.test(f); }
  function isSvg(f) { return /\.svg$/i.test(f); }
  function isPdf(f) { return /\.pdf$/i.test(f); }

  // Encode path for URLs (handle spaces & cyrillic)
  function encodePath(base, file) {
    return base + '/' + file.split('/').map(encodeURIComponent).join('/');
  }

  // Load and render markdown
  async function loadDescription(path, descFile, container) {
    if (!descFile) return;
    try {
      const url = encodePath(path, descFile);
      const res = await fetch(url);
      if (!res.ok) return;
      const text = await res.text();
      // Use marked.js if available, otherwise basic rendering
      if (window.marked) {
        container.innerHTML = window.marked.parse(text);
      } else {
        // Basic fallback: paragraphs from double newlines
        container.innerHTML = text
          .split(/\n\n+/)
          .map(function(p) { return '<p>' + p.replace(/\n/g, '<br>') + '</p>'; })
          .join('');
      }
    } catch(e) {}
  }

  // Build a project card
  function buildCard(project) {
    const card = document.createElement('div');
    card.className = 'project-card';

    // Header (always visible)
    const header = document.createElement('div');
    header.className = 'card-header';

    if (project.thumbnail) {
      const thumb = document.createElement('img');
      thumb.className = 'card-thumb';
      thumb.src = encodePath(project.path, project.thumbnail);
      thumb.alt = t(project.title);
      thumb.loading = 'lazy';
      header.appendChild(thumb);
    } else {
      const ph = document.createElement('div');
      ph.className = 'card-thumb-placeholder';
      ph.textContent = t(project.title).charAt(0).toUpperCase();
      header.appendChild(ph);
    }

    const title = document.createElement('div');
    title.className = 'card-title';
    title.textContent = t(project.title);
    header.appendChild(title);
    card.appendChild(header);

    // Content (shown on expand)
    const content = document.createElement('div');
    content.className = 'card-content';

    // Close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'card-close';
    closeBtn.textContent = '\u00d7';
    closeBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      card.classList.remove('expanded');
      card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
    content.appendChild(closeBtn);

    // Description container
    const descEl = document.createElement('div');
    descEl.className = 'card-description';
    content.appendChild(descEl);

    // Separate media types
    var images = (project.media || []).filter(function(f) { return isImage(f) || isSvg(f); });
    var videos = (project.media || []).filter(function(f) { return isVideo(f); });
    var pdfs = (project.media || []).filter(function(f) { return isPdf(f); });

    // Image gallery
    if (images.length > 0) {
      var galleryUrls = images.map(function(f) { return encodePath(project.path, f); });
      const galleryEl = document.createElement('div');
      galleryEl.className = 'card-gallery';
      images.forEach(function(file, idx) {
        const item = document.createElement('div');
        item.className = 'gallery-item' + (isSvg(file) ? ' gallery-item-svg' : '');
        const img = document.createElement('img');
        img.src = galleryUrls[idx];
        img.alt = t(project.title);
        img.loading = 'lazy';
        img.addEventListener('click', function(e) {
          e.stopPropagation();
          openLightbox(img.src, galleryUrls);
        });
        item.appendChild(img);
        galleryEl.appendChild(item);
      });
      content.appendChild(galleryEl);
    }

    // Videos
    videos.forEach(function(file) {
      const gallery = content.querySelector('.card-gallery') || (function() {
        const g = document.createElement('div');
        g.className = 'card-gallery';
        content.appendChild(g);
        return g;
      })();
      const item = document.createElement('div');
      item.className = 'gallery-item';
      const vid = document.createElement('video');
      vid.src = encodePath(project.path, file);
      vid.controls = true;
      vid.preload = 'metadata';
      vid.addEventListener('click', function(e) { e.stopPropagation(); });
      item.appendChild(vid);
      gallery.appendChild(item);
    });

    // PDF links
    if (pdfs.length > 0) {
      const filesDiv = document.createElement('div');
      filesDiv.className = 'card-files';
      pdfs.forEach(function(file) {
        const a = document.createElement('a');
        a.className = 'file-link';
        a.href = encodePath(project.path, file);
        a.target = '_blank';
        a.rel = 'noopener';
        // Show filename without path prefix
        var name = file.split('/').pop();
        a.textContent = '\u{1F4C4} ' + decodeURIComponent(name);
        a.addEventListener('click', function(e) { e.stopPropagation(); });
        filesDiv.appendChild(a);
      });
      content.appendChild(filesDiv);
    }

    // Empty state
    if (images.length === 0 && videos.length === 0 && pdfs.length === 0 && !project.description) {
      const empty = document.createElement('div');
      empty.className = 'card-empty';
      empty.textContent = lang === 'ru' ? '\u0421\u043a\u043e\u0440\u043e...' : lang === 'zh' ? '\u5373\u5c06\u63a8\u51fa...' : 'Coming soon...';
      content.appendChild(empty);
    }

    card.appendChild(content);

    // Click to expand
    header.addEventListener('click', function() {
      var wasExpanded = card.classList.contains('expanded');
      // Collapse all others in same grid
      card.parentElement.querySelectorAll('.project-card.expanded').forEach(function(c) {
        c.classList.remove('expanded');
      });
      if (!wasExpanded) {
        card.classList.add('expanded');
        // Load description on first expand
        if (!descEl._loaded && project.description) {
          descEl._loaded = true;
          loadDescription(project.path, project.description, descEl);
        }
        setTimeout(function() {
          card.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 50);
      }
    });

    return card;
  }

  // Main: fetch manifest and build
  async function init() {
    try {
      const res = await fetch('portfolio/manifest.json');
      if (!res.ok) throw new Error('manifest fetch failed');
      const data = await res.json();

      data.periods.forEach(function(period) {
        // Skip empty periods with no projects
        if (!period.projects || period.projects.length === 0) return;

        const section = document.createElement('div');
        section.className = 'period';

        const title = document.createElement('h2');
        title.className = 'period-title';
        title.textContent = t(period.title);
        section.appendChild(title);

        const grid = document.createElement('div');
        grid.className = 'project-grid';

        period.projects.forEach(function(project) {
          grid.appendChild(buildCard(project));
        });

        section.appendChild(grid);
        portfolioEl.appendChild(section);
      });
    } catch(e) {
      portfolioEl.innerHTML = '<p style="color:rgba(255,255,255,0.5);text-align:center;padding:40px;">Failed to load portfolio</p>';
    }
  }

  // Load marked.js from CDN, then init
  var script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
  script.onload = init;
  script.onerror = init; // fallback without markdown
  document.head.appendChild(script);
})();
