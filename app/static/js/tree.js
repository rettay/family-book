/* Family Book — D3 Tree Visualization */

(function() {
  'use strict';

  var svg;
  var g;
  var zoom;
  var treeData;
  var preferences = {
    show_names: true,
    show_birth_dates: false,
    show_country_flags: true,
    show_photos: true
  };
  var NODE_RADIUS = 30;
  var NODE_SPACING_X = 100;
  var NODE_SPACING_Y = 140;

  var root = document.getElementById('tree-root');
  var statusNode = document.getElementById('tree-status');

  function queryString(filters) {
    var params = new URLSearchParams();
    Object.keys(filters).forEach(function(key) {
      if (filters[key] && filters[key] !== 'all') {
        params.set(key, filters[key]);
      }
    });
    var query = params.toString();
    return query ? '?' + query : '';
  }

  function currentFilters() {
    return {
      living: document.getElementById('tree-filter-living').value,
      branch: document.getElementById('tree-filter-branch').value.trim(),
      residence_country: document.getElementById('tree-filter-residence-country').value.trim().toUpperCase(),
      birth_country: document.getElementById('tree-filter-birth-country').value.trim().toUpperCase()
    };
  }

  function syncPreferenceInputs() {
    document.getElementById('pref-show-names').checked = !!preferences.show_names;
    document.getElementById('pref-show-birth-dates').checked = !!preferences.show_birth_dates;
    document.getElementById('pref-show-country-flags').checked = !!preferences.show_country_flags;
    document.getElementById('pref-show-photos').checked = !!preferences.show_photos;
  }

  function readPreferenceInputs() {
    preferences = {
      show_names: document.getElementById('pref-show-names').checked,
      show_birth_dates: document.getElementById('pref-show-birth-dates').checked,
      show_country_flags: document.getElementById('pref-show-country-flags').checked,
      show_photos: document.getElementById('pref-show-photos').checked
    };
  }

  function setStatus(text) {
    statusNode.textContent = text;
  }

  async function loadPreferences() {
    var resp = await fetch('/api/tree/preferences');
    if (resp.status === 401) {
      window.location.href = '/login';
      return false;
    }
    preferences = await resp.json();
    syncPreferenceInputs();
    return true;
  }

  async function savePreferences() {
    readPreferenceInputs();
    var resp = await fetch('/api/tree/preferences', {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(preferences)
    });
    if (resp.status === 401) {
      window.location.href = '/login';
      return;
    }
    preferences = await resp.json();
    syncPreferenceInputs();
    render();
  }

  async function loadTree() {
    setStatus(document.body.dataset.loadingText || 'Loading...');
    var resp = await fetch('/api/tree' + queryString(currentFilters()));
    if (resp.status === 401) {
      window.location.href = '/login';
      return;
    }
    treeData = await resp.json();
    render();
  }

  async function init() {
    try {
      var loaded = await loadPreferences();
      if (!loaded) {
        return;
      }
      await loadTree();
    } catch (err) {
      document.getElementById('tree-page').textContent = root.dataset.loadError;
    }
  }

  function drawEmptyState(w, h) {
    g.append('text')
      .attr('x', w / 2)
      .attr('y', h / 2)
      .attr('text-anchor', 'middle')
      .attr('fill', '#6b6054')
      .text(root.dataset.emptyText);
    setStatus(root.dataset.statusTemplate.replace('{count}', '0'));
  }

  function buildTreeStructures() {
    var personsById = {};
    treeData.persons.forEach(function(person) {
      personsById[person.id] = person;
    });

    var childToParents = {};
    var parentToChildren = {};
    treeData.parent_child.forEach(function(parentChild) {
      if (!childToParents[parentChild.child_id]) {
        childToParents[parentChild.child_id] = [];
      }
      childToParents[parentChild.child_id].push(parentChild.parent_id);
      if (!parentToChildren[parentChild.parent_id]) {
        parentToChildren[parentChild.parent_id] = [];
      }
      parentToChildren[parentChild.parent_id].push(parentChild.child_id);
    });

    return {
      personsById: personsById,
      childToParents: childToParents,
      parentToChildren: parentToChildren
    };
  }

  function determineRootId(personsById, childToParents) {
    var rootId = treeData.root_id;
    if (!rootId || !personsById[rootId]) {
      var allChildIds = new Set(Object.keys(childToParents));
      var rootCandidates = treeData.persons.filter(function(person) {
        return !allChildIds.has(person.id);
      });
      rootId = rootCandidates.length > 0 ? rootCandidates[0].id : treeData.persons[0].id;
    }
    return rootId;
  }

  function layoutTree(rootId, parentToChildren) {
    var visited = new Set();
    var nodePositions = {};

    function buildHierarchy(rootNodeId) {
      var rootNode = {id: rootNodeId, children: [], depth: 0, x: 0, y: 0};
      var queue = [rootNode];
      visited.add(rootNodeId);

      while (queue.length > 0) {
        var node = queue.shift();
        var children = parentToChildren[node.id] || [];
        children.forEach(function(childId) {
          if (visited.has(childId)) {
            return;
          }
          visited.add(childId);
          var childNode = {id: childId, children: [], depth: node.depth + 1, parent: node};
          node.children.push(childNode);
          queue.push(childNode);
        });
      }

      return rootNode;
    }

    function applyLayout(node, xStart, y, maxDepth) {
      node.y = y;
      if (node.depth > maxDepth.value) {
        maxDepth.value = node.depth;
      }

      if (node.children.length === 0) {
        node.x = xStart + NODE_SPACING_X / 2;
        return xStart + NODE_SPACING_X;
      }

      var nextX = xStart;
      node.children.forEach(function(child) {
        nextX = applyLayout(child, nextX, y + NODE_SPACING_Y, maxDepth);
      });

      var first = node.children[0];
      var last = node.children[node.children.length - 1];
      node.x = (first.x + last.x) / 2;
      return nextX;
    }

    var rootNode = buildHierarchy(rootId);
    var maxDepth = {value: 0};
    applyLayout(rootNode, 0, 60, maxDepth);

    var allNodes = [];
    function collectNodes(node) {
      allNodes.push(node);
      nodePositions[node.id] = {x: node.x, y: node.y};
      node.children.forEach(collectNodes);
    }
    collectNodes(rootNode);

    var unvisited = treeData.persons.filter(function(person) {
      return !visited.has(person.id);
    });
    var ux = 0;
    unvisited.forEach(function(person) {
      var detachedNode = {
        id: person.id,
        children: [],
        depth: maxDepth.value + 1,
        x: ux,
        y: (maxDepth.value + 1) * NODE_SPACING_Y + 60
      };
      allNodes.push(detachedNode);
      nodePositions[person.id] = {x: detachedNode.x, y: detachedNode.y};
      ux += NODE_SPACING_X;
    });

    return {allNodes: allNodes, nodePositions: nodePositions};
  }

  function renderNode(node, person) {
    var nodeGroup = g.append('g')
      .attr('class', 'person-node' + (person.branch ? ' person-node--branch-' + person.branch : ''))
      .attr('data-id', person.id)
      .attr('transform', 'translate(' + node.x + ',' + node.y + ')')
      .style('cursor', 'pointer');

    var showPhoto = preferences.show_photos && person.photo_url;
    if (showPhoto) {
      var clipId = 'clip-' + person.id.replace(/[^a-zA-Z0-9]/g, '');
      var defs = nodeGroup.append('defs');
      defs.append('clipPath')
        .attr('id', clipId)
        .append('circle')
        .attr('r', NODE_RADIUS);
      nodeGroup.append('image')
        .attr('href', '/api/media/' + person.photo_url + '/file')
        .attr('x', -NODE_RADIUS)
        .attr('y', -NODE_RADIUS)
        .attr('width', NODE_RADIUS * 2)
        .attr('height', NODE_RADIUS * 2)
        .attr('clip-path', 'url(#' + clipId + ')')
        .attr('preserveAspectRatio', 'xMidYMid slice');
      nodeGroup.append('circle')
        .attr('class', 'photo-clip')
        .attr('r', NODE_RADIUS)
        .attr('fill', 'none')
        .attr('stroke', 'white')
        .attr('stroke-width', 2);
    } else {
      nodeGroup.append('circle')
        .attr('class', 'photo-clip')
        .attr('r', NODE_RADIUS);
      nodeGroup.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '0.35em')
        .attr('fill', '#2d5016')
        .attr('font-size', '14px')
        .attr('font-weight', '600')
        .attr('pointer-events', 'none')
        .text(person.display_name.substring(0, 2));
    }

    nodeGroup.append('circle')
      .attr('class', 'tap-target')
      .attr('r', NODE_RADIUS + 10);

    if (preferences.show_names) {
      nodeGroup.append('text')
        .attr('class', 'name-label')
        .attr('dy', NODE_RADIUS + 16)
        .text(person.display_name);
    }

    if (preferences.show_birth_dates && person.birth_date_raw) {
      nodeGroup.append('text')
        .attr('class', 'rel-label')
        .attr('dy', NODE_RADIUS + (preferences.show_names ? 32 : 18))
        .text(person.birth_date_raw);
    }

    if (preferences.show_country_flags && person.residence_country_code) {
      nodeGroup.append('text')
        .attr('class', 'rel-label')
        .attr('dy', NODE_RADIUS + (preferences.show_names || preferences.show_birth_dates ? 46 : 18))
        .text(countryFlag(person.residence_country_code));
    }

    nodeGroup.on('click', function() {
      openPersonSidebar(person.id);
    });

    nodeGroup.on('dblclick', function() {
      window.location.href = '/people/' + person.id;
    });
  }

  function render() {
    var container = document.getElementById('tree-page');
    var w = container.clientWidth;
    var h = container.clientHeight;

    svg = d3.select('#tree-svg')
      .attr('width', w)
      .attr('height', h);
    svg.selectAll('*').remove();

    g = svg.append('g');

    zoom = d3.zoom()
      .scaleExtent([0.2, 3])
      .on('zoom', function(event) {
        g.attr('transform', event.transform);
      });
    svg.call(zoom);

    if (!treeData || !treeData.persons || treeData.persons.length === 0) {
      drawEmptyState(w, h);
      return;
    }

    var structures = buildTreeStructures();
    var rootId = determineRootId(structures.personsById, structures.childToParents);
    var layout = layoutTree(rootId, structures.parentToChildren);

    var lineGen = d3.line().curve(d3.curveBumpY);
    layout.allNodes.forEach(function(node) {
      if (node.children) {
        node.children.forEach(function(child) {
          g.append('path')
            .attr('class', 'parent-child-line')
            .attr('d', lineGen([[node.x, node.y + NODE_RADIUS], [child.x, child.y - NODE_RADIUS]]));
        });
      }
    });

    treeData.partnerships.forEach(function(partnership) {
      var posA = layout.nodePositions[partnership.person_a_id];
      var posB = layout.nodePositions[partnership.person_b_id];
      if (!posA || !posB) {
        return;
      }
      var dissolved = partnership.status === 'dissolved' || partnership.status === 'separated';
      g.append('line')
        .attr('class', 'partnership-line' + (dissolved ? ' partnership-line--dissolved' : ''))
        .attr('x1', posA.x)
        .attr('y1', posA.y)
        .attr('x2', posB.x)
        .attr('y2', posB.y);
    });

    layout.allNodes.forEach(function(node) {
      var person = structures.personsById[node.id];
      if (person) {
        renderNode(node, person);
      }
    });

    var bounds = g.node().getBBox();
    var dx = w / 2 - (bounds.x + bounds.width / 2);
    var dy = h / 2 - (bounds.y + bounds.height / 2);
    var scale = Math.min(w / (bounds.width + 100), h / (bounds.height + 100), 1);
    svg.call(zoom.transform, d3.zoomIdentity.translate(dx, dy).scale(scale));

    setStatus(root.dataset.statusTemplate.replace('{count}', String(treeData.persons.length)));
  }

  function openPersonSidebar(personId) {
    var sidebar = document.getElementById('person-sidebar');
    sidebar.classList.add('person-sidebar--open');
    htmx.ajax('GET', '/people/' + personId + '/card', {target: '#sidebar-content', swap: 'innerHTML'});
  }

  function countryFlag(code) {
    if (!code || code.length !== 2) {
      return '';
    }
    var offset = 127397;
    return String.fromCodePoint(code.charCodeAt(0) + offset, code.charCodeAt(1) + offset);
  }

  window.treeZoomIn = function() {
    if (svg && zoom) {
      svg.transition().call(zoom.scaleBy, 1.3);
    }
  };
  window.treeZoomOut = function() {
    if (svg && zoom) {
      svg.transition().call(zoom.scaleBy, 0.7);
    }
  };
  window.treeReset = function() {
    if (treeData) {
      render();
    }
  };
  window.closeSidebar = function() {
    document.getElementById('person-sidebar').classList.remove('person-sidebar--open');
  };

  document.getElementById('save-tree-preferences').addEventListener('click', savePreferences);
  document.getElementById('apply-tree-filters').addEventListener('click', loadTree);
  document.getElementById('reset-tree-filters').addEventListener('click', function() {
    document.getElementById('tree-filter-living').value = 'all';
    document.getElementById('tree-filter-branch').value = '';
    document.getElementById('tree-filter-residence-country').value = '';
    document.getElementById('tree-filter-birth-country').value = '';
    loadTree();
  });

  var resizeTimeout;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function() {
      if (treeData) {
        render();
      }
    }, 250);
  });

  init();
})();
