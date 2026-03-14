document.addEventListener('DOMContentLoaded', () => {
  console.log('[GSoC Globe] app loaded');

  const map = new maplibregl.Map({
    container: 'map',
    style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
    center: [20, 20],
    zoom: 1.8,
    attributionControl: false
  });

  let isUserInteracting = false;

  map.on('style.load', () => {
    // Enable globe projection
    map.setProjection({ type: 'globe' });

    // Set atmosphere
    map.setSky({
      'sky-color': '#000510',
      'sky-horizon-blend': 0.04,
      'horizon-color': '#0a0a0f',
      'fog-color': '#0a0a0f',
      'fog-ground-blend': 0.5,
      'atmosphere-blend': ['interpolate', ['linear'], ['zoom'], 0, 1, 5, 0]
    });
  });

  map.on('load', () => {
    // Auto-rotation — shift longitude so globe spins on vertical axis
    function rotate() {
      if (!isUserInteracting) {
        const center = map.getCenter();
        const zoom = map.getZoom();

        // Base speed at zoom 0 is 0.05. It halves for every zoom level.
        // e.g. Zoom 1 = 0.025, Zoom 2 = 0.0125, Zoom 4 = 0.003
        const speed = 0.1 / Math.pow(2, zoom);

        map.setCenter([(center.lng + speed) % 360, center.lat]);
      }
      requestAnimationFrame(rotate);
    }
    requestAnimationFrame(rotate);

    // --- Task 3: Load orgs and plot markers ---
    fetch(`./data/orgs.json?v=${Date.now()}`)
      .then(res => res.json())
      .then(orgsData => {
        window.orgsData = orgsData;

        const geojson = {
          type: 'FeatureCollection',
          features: orgsData.map(org => ({
            type: 'Feature',
            geometry: { type: 'Point', coordinates: [org.lng, org.lat] },
            properties: {
              ...org,
              yearsCount: org.years.length,
              years: JSON.stringify(org.years),
              techStack: JSON.stringify(org.techStack)
            }
          }))
        };

        // Clustered GeoJSON source
        map.addSource('orgs', {
          type: 'geojson',
          data: geojson,
          cluster: true,
          clusterMaxZoom: 4,
          clusterRadius: 40
        });

        // Cluster circle layer
        map.addLayer({
          id: 'clusters',
          type: 'circle',
          source: 'orgs',
          filter: ['has', 'point_count'],
          paint: {
            'circle-radius': 18,
            'circle-color': '#00f5ff',
            'circle-opacity': 0.7
          }
        });

        // Cluster count text layer
        map.addLayer({
          id: 'cluster-count',
          type: 'symbol',
          source: 'orgs',
          filter: ['has', 'point_count'],
          layout: {
            'text-field': ['get', 'point_count_abbreviated'],
            'text-size': 12,
            'text-font': ['literal', ['Open Sans Bold']]
          },
          paint: {
            'text-color': '#0a0a0f'
          }
        });

        // Individual org circle layer
        map.addLayer({
          id: 'org-points',
          type: 'circle',
          source: 'orgs',
          filter: ['!', ['has', 'point_count']],
          paint: {
            'circle-radius': ['interpolate', ['linear'], ['get', 'yearsCount'], 1, 5, 10, 12],
            'circle-color': [
              'match', ['get', 'category'],
              'AI/ML', '#00f5ff',
              'Web', '#00ff41',
              'Security', '#ff3b3b',
              'Cloud', '#a78bfa',
              'Mobile', '#fbbf24',
              'Science', '#34d399',
              'Education', '#fb7185',
              'DevTools', '#ff6b35',
              '#ffffff'
            ],
            'circle-opacity': 0.9,
            'circle-stroke-width': 1.5,
            'circle-stroke-color': 'rgba(255,255,255,0.2)'
          }
        });

        // --- Task 8: Dynamic Connections ---
        const googleHQ = [-122.0841, 37.4223]; // Mountain View, CA

        // Add persistent marker for Google HQ
        const hqEl = document.createElement('div');
        hqEl.className = 'google-hq-marker';
        hqEl.innerHTML = '<span class="hq-dot"></span>Google HQ';
        new maplibregl.Marker({ element: hqEl })
          .setLngLat(googleHQ)
          .addTo(map);

        map.addSource('route', {
          type: 'geojson',
          data: { type: 'FeatureCollection', features: [] }
        });

        map.addLayer({
          id: 'route-line',
          type: 'line',
          source: 'route',
          layout: {
            'line-join': 'round',
            'line-cap': 'round'
          },
          paint: {
            'line-color': '#00f5ff',
            'line-width': 2,
            'line-dasharray': [0, 4, 3],
            'line-opacity': 0.8
          }
        });

        // Cluster click — zoom in and clear route
        map.on('click', 'clusters', (e) => {
          const coords = e.features[0].geometry.coordinates;
          map.flyTo({ center: coords, zoom: map.getZoom() + 2 });
          map.getSource('route').setData({ type: 'FeatureCollection', features: [] });
        });

        // Org point click — flyTo & open detail drawer
        map.on('click', 'org-points', (e) => {
          const props = e.features[0].properties;
          console.log('Org clicked:', props);

          map.flyTo({
            center: e.lngLat,
            zoom: 4,
            bearing: 0, // Reset bearing to face North naturally for reading
            pitch: 0,
            duration: 1200
          });

          openDetailPanel(props);
        });

        // Pointer cursor on hover
        map.on('mouseenter', 'clusters', () => { map.getCanvas().style.cursor = 'pointer'; });
        map.on('mouseleave', 'clusters', () => { map.getCanvas().style.cursor = ''; });

        // --- Task 9: Hover Tooltips/Modals ---
        const hoverPopup = new maplibregl.Popup({
          closeButton: false,
          closeOnClick: false,
          offset: 15
        });

        map.on('mouseenter', 'org-points', (e) => {
          map.getCanvas().style.cursor = 'pointer';

          const coords = e.features[0].geometry.coordinates.slice();
          const props = e.features[0].properties;

          // Ensure popup appears over the correct copy of the point if zooming out
          while (Math.abs(e.lngLat.lng - coords[0]) > 180) {
            coords[0] += e.lngLat.lng > coords[0] ? 360 : -360;
          }

          const html = `
            <div class="popup-title">${props.name}</div>
            <span class="popup-cat" style="color: ${catColors[props.category] || '#fff'}">${props.category}</span>
          `;

          hoverPopup.setLngLat(coords).setHTML(html).addTo(map);
        });

        map.on('mouseleave', 'org-points', () => {
          map.getCanvas().style.cursor = '';
          hoverPopup.remove();
        });

        // --- Task 7: Enhanced Global Search (Fuse.js) ---
        const fuse = new Fuse(orgsData, {
          keys: ['name', 'category', 'techStack', 'country'],
          threshold: 0.3
        });

        const searchInput = document.getElementById('global-search');
        const searchStats = document.getElementById('search-stats');
        const searchClear = document.getElementById('search-clear');
        const searchDropdown = document.getElementById('search-dropdown');

        function performSearch() {
          const query = searchInput.value.trim();
          let results = orgsData;

          if (query !== '') {
            results = fuse.search(query).map(result => result.item);
            searchStats.textContent = `Found ${results.length}`;
            searchStats.classList.remove('hidden');
            searchClear.classList.remove('hidden');
            searchDropdown.classList.remove('hidden');

            // Populate dropdown
            searchDropdown.innerHTML = '';
            if (results.length > 0) {
              results.slice(0, 10).forEach(org => { // limit dropdown to top 10
                const item = document.createElement('div');
                item.className = 'search-result-item';
                item.innerHTML = `
                  <span class="search-result-name">${org.name}</span>
                  <span class="search-result-cat" style="background: ${catColors[org.category] || '#fff'}">${org.category}</span>
                `;
                item.addEventListener('click', () => {
                  // Fly to org
                  map.flyTo({
                    center: [org.lng, org.lat],
                    zoom: 4,
                    bearing: 0,
                    pitch: 0,
                    duration: 1200
                  });
                  openDetailPanel(org);

                  // Hide dropdown but keep geojson filtered
                  searchDropdown.classList.add('hidden');
                });
                searchDropdown.appendChild(item);
              });
            } else {
              searchDropdown.innerHTML = '<div style="padding:10px 16px; color:var(--muted); font-size:12px">No matches found</div>';
            }
          } else {
            searchStats.classList.add('hidden');
            searchClear.classList.add('hidden');
            searchDropdown.classList.add('hidden');
            searchDropdown.innerHTML = '';
          }

          // Update Globe geojson
          const searchGeojson = {
            type: 'FeatureCollection',
            features: results.map(org => ({
              type: 'Feature',
              geometry: { type: 'Point', coordinates: [org.lng, org.lat] },
              properties: {
                ...org,
                yearsCount: org.years.length,
                years: JSON.stringify(org.years),
                techStack: JSON.stringify(org.techStack)
              }
            }))
          };

          if (map.getSource('orgs')) {
            map.getSource('orgs').setData(searchGeojson);
          }
        }

        searchInput.addEventListener('input', performSearch);

        // Hide dropdown when clicking outside
        document.addEventListener('click', (e) => {
          if (!document.getElementById('search-wrapper').contains(e.target)) {
            searchDropdown.classList.add('hidden');
          }
        });

        // Show dropdown on input focus if there's a typed query
        searchInput.addEventListener('focus', () => {
          if (searchInput.value.trim() !== '') {
            searchDropdown.classList.remove('hidden');
          }
        });

        searchClear.addEventListener('click', () => {
          searchInput.value = '';
          performSearch();
        });
      });
  });

  // --- Task 10: Shortlist State ---
  function getShortlist() {
    return JSON.parse(localStorage.getItem('gsocShortlist') || '[]');
  }

  function toggleShortlist(orgName) {
    let list = getShortlist();
    if (list.includes(orgName)) {
      list = list.filter(n => n !== orgName);
    } else {
      list.push(orgName);
    }
    localStorage.setItem('gsocShortlist', JSON.stringify(list));
    return list.includes(orgName);
  }

  // --- Task 5: Detail Panel Logic ---
  const detailPanel = document.getElementById('detail-panel');
  const detailTitle = document.getElementById('detail-title');
  const detailBody = document.getElementById('detail-body');
  const detailClose = document.getElementById('detail-close');

  const catColors = {
    'AI/ML': '#00f5ff',
    'Web': '#00ff41',
    'Security': '#ff3b3b',
    'Cloud': '#a78bfa',
    'Mobile': '#fbbf24',
    'Science': '#34d399',
    'Education': '#fb7185',
    'DevTools': '#ff6b35',
  };

  function openDetailPanel(props) {
    // Parse JSON strings from MapLibre properties, or use directly if object
    const years = typeof props.years === 'string' ? JSON.parse(props.years) : props.years;
    const techStack = typeof props.techStack === 'string' ? JSON.parse(props.techStack) : props.techStack;

    detailTitle.textContent = props.name;

    // Timeline graphic
    let timelineHtml = '<pre class="timeline-bar">';
    for (let y = 2016; y <= 2026; y++) {
      timelineHtml += years.includes(y) ? `<span style="color:var(--cyan)">█</span>` : `░`;
    }
    timelineHtml += '</pre>';

    // Stack tags
    const tagsHtml = `<div class="tag-list">${techStack.map(t => `<span class="stack-tag">${t}</span>`).join('')}</div>`;

    detailBody.innerHTML = `
      <div class="detail-badge" style="color: ${catColors[props.category] || '#fff'}; border-color: ${catColors[props.category] || '#fff'}">
        ${props.category}
      </div>
      <div class="detail-row">Location: <span>${props.country}</span></div>
      <div class="detail-row">Slots (2024): <span>${props.slots}</span></div>
      
      <div style="margin-top:20px">
        <div class="detail-row">GSoC History:</div>
        ${timelineHtml}
        <div class="detail-row" style="font-size:10px; margin-top:4px">2016 <span style="float:right">2026</span></div>
      </div>

      <div style="margin-top:20px">
        <div class="detail-row">Tech Stack:</div>
        ${tagsHtml}
      </div>

      <div class="detail-links">
        <a href="${props.website}" target="_blank" class="detail-link-btn">↗ Website</a>
        <a href="${props.github}" target="_blank" class="detail-link-btn">↗ GitHub</a>
        <a href="${props.gsocPage}" target="_blank" class="detail-link-btn">↗ GSoC Page</a>
        <a href="${props.github}/issues?q=good-first-issue" target="_blank" class="detail-link-btn" style="color:var(--green); border-color:var(--green)">
          &gt; Good First Issues
        </a>
      </div>

      <!-- Task 10 Button state -->
      <button id="detail-shortlist-btn" class="shortlist-btn"></button>
    `;

    // Initialize button state
    const shortlistBtn = document.getElementById('detail-shortlist-btn');
    const isShortlisted = getShortlist().includes(props.name);

    if (isShortlisted) {
      shortlistBtn.classList.add('added');
      shortlistBtn.textContent = '✓ SHORTLISTED';
    } else {
      shortlistBtn.classList.remove('added');
      shortlistBtn.textContent = '⊕ ADD TO SHORTLIST';
    }

    // Wire toggle
    shortlistBtn.onclick = () => {
      const nowShortlisted = toggleShortlist(props.name);
      if (nowShortlisted) {
        shortlistBtn.classList.add('added');
        shortlistBtn.textContent = '✓ SHORTLISTED';
      } else {
        shortlistBtn.classList.remove('added');
        shortlistBtn.textContent = '⊕ ADD TO SHORTLIST';
      }
    };

    detailPanel.classList.remove('collapsed');

    // --- Task 8: Draw Route ---
    if (window.turf && map.getSource('route')) {
      const start = turf.point([props.lng, props.lat]);
      const end = turf.point([-122.0841, 37.4223]); // Google HQ

      // Calculate great circle route
      const greatCircle = turf.greatCircle(start, end, { properties: { name: 'Route to Google' } });

      map.getSource('route').setData({
        type: 'FeatureCollection',
        features: [greatCircle]
      });
    }
  }

  detailClose.addEventListener('click', () => {
    detailPanel.classList.add('collapsed');
    if (map.getSource('route')) {
      map.getSource('route').setData({ type: 'FeatureCollection', features: [] });
    }
  });

  // User interaction toggles
  map.on('mousedown', () => { isUserInteracting = true; });
  map.on('touchstart', () => { isUserInteracting = true; });
  map.on('mouseup', () => { isUserInteracting = false; });
  map.on('touchend', () => { isUserInteracting = false; });

  // --- Task 4 & 6: Filter Panel UI & Logic ---
  const filterPanel = document.getElementById('filter-panel');
  const filterOpenBtn = document.getElementById('filter-open-btn');
  const filterToggle = document.getElementById('filter-toggle');
  const yearPills = document.getElementById('year-pills');
  const categoryPills = document.getElementById('category-pills');
  const techSearch = document.getElementById('tech-search');
  const techTagsContainer = document.getElementById('tech-tags');
  const veteranToggle = document.getElementById('veteran-toggle');
  const clearFiltersBtn = document.getElementById('clear-filters');
  const filterCountBadge = document.getElementById('filter-count');
  const presetAimlBtn = document.getElementById('preset-aiml');

  // Filter State
  let filters = {
    years: [],
    categories: [],
    techStack: [],
    veteranOnly: false
  };

  function applyFilters() {
    if (!window.orgsData) return;

    // Filter the orgs
    const filteredOrgs = window.orgsData.filter(org => {
      // Veteran check (> 5 years)
      if (filters.veteranOnly && org.years.length < 5) return false;

      // Years match (needs to participate in ALL selected years, or ANY? PRD usually implies ANY for multi-select, but let's do ANY for years)
      if (filters.years.length > 0) {
        if (!filters.years.some(y => org.years.includes(y))) return false;
      }

      // Categories match (ANY)
      if (filters.categories.length > 0) {
        if (!filters.categories.includes(org.category)) return false;
      }

      // Tech Stack match (has ANY of the selected tags)
      if (filters.techStack.length > 0) {
        const orgTech = org.techStack.map(t => t.toLowerCase());
        if (!filters.techStack.some(t => orgTech.includes(t.toLowerCase()))) return false;
      }

      return true;
    });

    // Update map data
    const newGeojson = {
      type: 'FeatureCollection',
      features: filteredOrgs.map(org => ({
        type: 'Feature',
        geometry: { type: 'Point', coordinates: [org.lng, org.lat] },
        properties: {
          ...org,
          yearsCount: org.years.length,
          years: JSON.stringify(org.years),
          techStack: JSON.stringify(org.techStack)
        }
      }))
    };

    // Safety check - source might not be added yet if this runs too early
    if (map.getSource('orgs')) {
      map.getSource('orgs').setData(newGeojson);
    }

    // Update UI Badge
    const activeFilterCount = filters.years.length + filters.categories.length + filters.techStack.length + (filters.veteranOnly ? 1 : 0);
    if (activeFilterCount > 0) {
      filterCountBadge.textContent = `(${filteredOrgs.length} results)`;
      filterCountBadge.classList.remove('hidden');
    } else {
      filterCountBadge.classList.add('hidden');
    }
  }

  // Render year pills & attach handlers
  for (let year = 2016; year <= 2026; year++) {
    const pill = document.createElement('button');
    pill.className = 'pill';
    pill.textContent = year;
    pill.addEventListener('click', () => {
      pill.classList.toggle('active');
      if (pill.classList.contains('active')) {
        filters.years.push(year);
      } else {
        filters.years = filters.years.filter(y => y !== year);
      }
      applyFilters();
    });
    yearPills.appendChild(pill);
  }

  // Render category pills & attach handlers
  ['AI/ML', 'Web', 'Security', 'Cloud', 'Mobile', 'Science', 'Education', 'DevTools'].forEach(cat => {
    const pill = document.createElement('button');
    pill.className = 'pill';
    pill.textContent = cat;
    pill.addEventListener('click', () => {
      pill.classList.toggle('active');
      if (pill.classList.contains('active')) {
        filters.categories.push(cat);
      } else {
        filters.categories = filters.categories.filter(c => c !== cat);
      }
      applyFilters();
    });
    categoryPills.appendChild(pill);
  });

  // Tech stack search
  techSearch.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && techSearch.value.trim() !== '') {
      const tag = techSearch.value.trim();
      if (!filters.techStack.includes(tag)) {
        filters.techStack.push(tag);

        // Render tag
        const tagEl = document.createElement('span');
        tagEl.className = 'tech-tag';
        tagEl.innerHTML = `${tag} <span class="remove">✕</span>`;
        tagEl.querySelector('.remove').addEventListener('click', () => {
          filters.techStack = filters.techStack.filter(t => t !== tag);
          tagEl.remove();
          applyFilters();
        });
        techTagsContainer.appendChild(tagEl);

        applyFilters();
      }
      techSearch.value = '';
    }
  });

  // Veteran toggle
  veteranToggle.addEventListener('change', (e) => {
    filters.veteranOnly = e.target.checked;
    applyFilters();
  });

  // Clear all filters
  clearFiltersBtn.addEventListener('click', () => {
    filters = { years: [], categories: [], techStack: [], veteranOnly: false };
    document.querySelectorAll('.pill.active').forEach(p => p.classList.remove('active'));
    techTagsContainer.innerHTML = '';
    veteranToggle.checked = false;
    applyFilters();
  });

  // Preset: AI/ML 2026
  presetAimlBtn.addEventListener('click', () => {
    clearFiltersBtn.click(); // Reset first

    // Simulate clicks on the specific pills
    [...yearPills.children].find(p => p.textContent === '2026').click();
    [...categoryPills.children].find(p => p.textContent === 'AI/ML').click();
  });

  // Toggle handlers for panel
  filterToggle.addEventListener('click', () => {
    filterPanel.classList.add('collapsed');
    filterOpenBtn.classList.remove('hidden');
  });

  filterOpenBtn.addEventListener('click', () => {
    filterPanel.classList.remove('collapsed');
    filterOpenBtn.classList.add('hidden');
  });
});
