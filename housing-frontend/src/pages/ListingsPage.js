import React, { useEffect, useState } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Typography,
  TextField,
  Chip,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import api from '../api';

function ListingsPage() {
  const [items, setItems] = useState([]);
  const [filteredItems, setFilteredItems] = useState([]);
  const [search, setSearch] = useState('');
  const [flagFilter, setFlagFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [tagInputs, setTagInputs] = useState({});
  const [confirmDelete, setConfirmDelete] = useState({ open: false, id: null, tag: '' });

  useEffect(() => {
    fetchData();
  }, [currentPage]);

  useEffect(() => {
    (async () => {
      await applyFilters();
    })();
  }, [items, search, flagFilter]);

  const fetchData = async () => {
    try {
      const response = await api.get(`/new_analysis/${currentPage}`, {
        params: { per_page: 10 },
      });
      const rawData = response.data.data;
      const filtered = rawData.filter(
        item =>
          item.description &&
          item.description !== 'No description found' &&
          item.description !== 'No description available'
      );
      setItems(filtered);
      setTotalPages(response.data.total_pages);
    } catch (error) {
      console.error('Fetch failed:', error);
    }
  };

  const searchByTag = async query => {
    try {
      const response = await api.get('/search_tag', {
        params: { query },
      });
      return response.data;
    } catch (error) {
      console.error('Search by tag failed:', error);
      return [];
    }
  };

  const applyFilters = async () => {
    let filtered = [...items];
    if (search.trim() !== '') {
      filtered = await searchByTag(search.trim());
    }
    if (flagFilter === 'flagged') {
      filtered = filtered.filter(item => item.flagged === true);
    } else if (flagFilter === 'not_flagged') {
      filtered = filtered.filter(item => item.flagged === false);
    }
    setFilteredItems(filtered);
  };

  const toggleText = (id, type) => {
    const short = document.getElementById(`${type}-short-${id}`);
    const full = document.getElementById(`${type}-full-${id}`);
    if (!short || !full) return;
    const isHidden = full.style.display === 'none';
    short.style.display = isHidden ? 'none' : 'inline';
    full.style.display = isHidden ? 'inline' : 'none';
  };

  const shorten = (text = '') =>
    text.length > 150 ? text.slice(0, 150) + '...' : text;

  const getAnalysisText = item => {
    if (!item.analysis) return '';
    try {
      const parsed = JSON.parse(item.analysis);
      return parsed.analysis || '';
    } catch (err) {
      console.error('Parse error:', item.analysis);
      return '';
    }
  };

  const handleFlag = async (id, value) => {
    try {
      await api.post(`/human_feedback/${id}`, {
        is_matched: value,
      });
      fetchData();
    } catch (err) {
      console.error('Flag update failed:', err);
    }
  };

  const handleAddTag = async id => {
    const newTag = tagInputs[id]?.trim();
    if (!newTag) return;
    try {
      await api.post(`/add_tag/${id}`, {
        tag: [newTag],
      });
      setTagInputs(prev => ({ ...prev, [id]: '' }));
      fetchData();
    } catch (err) {
      console.error('Tag add failed:', err);
    }
  };

  const handleDeleteTag = (id, tag) => {
    setConfirmDelete({ open: true, id, tag });
  };

  const confirmDeleteTag = async () => {
    try {
      await api.post(`/delete_tag/${confirmDelete.id}`, { tag: confirmDelete.tag });
      setConfirmDelete({ open: false, id: null, tag: '' });
      fetchData();
    } catch (err) {
      console.error('Tag delete failed:', err);
      setConfirmDelete({ open: false, id: null, tag: '' });
    }
  };

  const cancelDeleteTag = () => {
    setConfirmDelete({ open: false, id: null, tag: '' });
  };

  return (
    <Box sx={{ p: 4, backgroundColor: '#f6f8fa', minHeight: '100vh', fontFamily: 'Poppins, sans-serif' }}>
      <Typography variant="h4" align="center" color="#1976d2" gutterBottom>
        Discriminatory Listings
      </Typography>

      <Box display="flex" flexWrap="wrap" justifyContent="center" gap={2} mb={2}>
        <TextField
          placeholder="🔍 Search by tags"
          variant="outlined"
          size="small"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          sx={{ width: 280 }}
        />
        <FormControl variant="outlined" size="small" sx={{ minWidth: 150 }}>
          <InputLabel id="flag-filter-label">Flag Filter</InputLabel>
          <Select
            labelId="flag-filter-label"
            value={flagFilter}
            onChange={(e) => setFlagFilter(e.target.value)}
            label="Flag Filter"
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="flagged">Flagged</MenuItem>
            <MenuItem value="not_flagged">Not Flagged</MenuItem>
          </Select>
        </FormControl>
        <Button variant="contained" onClick={applyFilters}>
          Apply Filters
        </Button>
      </Box>

      <TableContainer component={Paper} sx={{ borderRadius: 2, border: '1px solid #ddd' }}>
        <Table>
          <TableHead sx={{ backgroundColor: '#1976d2' }}>
            <TableRow>
              <TableCell sx={{ color: '#fff', maxWidth: 140 }}>URL</TableCell>
              <TableCell sx={{ color: '#fff' }}>Description</TableCell>
              <TableCell sx={{ color: '#fff' }}>Analysis</TableCell>
              <TableCell sx={{ color: '#fff' }} align="center">Flagged</TableCell>
              <TableCell sx={{ color: '#fff' }} align="center">Not Flagged</TableCell>
              <TableCell sx={{ color: '#fff' }}>Tags</TableCell>
              <TableCell sx={{ color: '#fff', minWidth: 220 }}>Add Tag</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredItems.map((item) => (
              <TableRow key={item.id}>
                <TableCell sx={{ maxWidth: 140, wordWrap: 'break-word' }}>
                  <a href={item.url} target="_blank" rel="noreferrer">{item.url}</a>
                </TableCell>
                <TableCell>
                  <Box sx={{ minHeight: '80px' }}>
                    <span id={`desc-short-${item.id}`}>
                      {shorten(item.description)}{' '}
                      {item.description.length > 150 && (
                        <a href="#!" onClick={() => toggleText(item.id, 'desc')}>More</a>
                      )}
                    </span>
                    <span id={`desc-full-${item.id}`} style={{ display: 'none' }}>
                      {item.description}{' '}
                      <a href="#!" onClick={() => toggleText(item.id, 'desc')}>Hide</a>
                    </span>
                  </Box>
                </TableCell>
                <TableCell>
                  <Box sx={{ minHeight: '60px' }}>
                    <span id={`analysis-short-${item.id}`}>
                      {shorten(getAnalysisText(item))}{' '}
                      {getAnalysisText(item).length > 150 && (
                        <a href="#!" onClick={() => toggleText(item.id, 'analysis')}>More</a>
                      )}
                    </span>
                    <span id={`analysis-full-${item.id}`} style={{ display: 'none' }}>
                      {getAnalysisText(item)}{' '}
                      <a href="#!" onClick={() => toggleText(item.id, 'analysis')}>Hide</a>
                    </span>
                  </Box>
                </TableCell>
                <TableCell align="center">
                  <input
                    type="radio"
                    name={`matched-${item.id}`}
                    checked={item.flagged === true}
                    onChange={() => handleFlag(item.id, true)}
                  />
                </TableCell>
                <TableCell align="center">
                  <input
                    type="radio"
                    name={`matched-${item.id}`}
                    checked={item.flagged === false}
                    onChange={() => handleFlag(item.id, false)}
                  />
                </TableCell>
                <TableCell>
                  {(item.comments || []).flat().map((tag, index) => (
                    <Chip
                      key={index}
                      label={tag}
                      size="small"
                      sx={{ m: 0.5, backgroundColor: '#e0f0ff', fontWeight: 500 }}
                      onDelete={() => handleDeleteTag(item.id, tag)}
                      deleteIcon={<CloseIcon sx={{ fontSize: '1rem' }} />}
                    />
                  ))}
                </TableCell>
                <TableCell sx={{ minWidth: 220 }}>
                  <Box display="flex" gap={1} alignItems="center">
                    <TextField
                      size="small"
                      placeholder="Add tag"
                      value={tagInputs[item.id] || ''}
                      onChange={(e) =>
                        setTagInputs((prev) => ({ ...prev, [item.id]: e.target.value }))
                      }
                      fullWidth
                    />
                    <Button variant="contained" size="small" onClick={() => handleAddTag(item.id)}>
                      Add
                    </Button>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Box display="flex" justifyContent="center" mt={3} gap={2} flexWrap="wrap">
        <Button
          variant="contained"
          disabled={currentPage === 1}
          onClick={() => setCurrentPage((p) => p - 1)}
        >
          Previous
        </Button>
        <Typography variant="body1" fontWeight={500}>
          Page: {currentPage} / {totalPages}
        </Typography>
        <Button
          variant="contained"
          disabled={currentPage === totalPages}
          onClick={() => setCurrentPage((p) => p + 1)}
        >
          Next
        </Button>
      </Box>

      <Dialog open={confirmDelete.open} onClose={cancelDeleteTag}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          Are you sure you want to delete tag: <strong>{confirmDelete.tag}</strong>?
        </DialogContent>
        <DialogActions>
          <Button onClick={cancelDeleteTag} color="primary">Cancel</Button>
          <Button onClick={confirmDeleteTag} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default ListingsPage;
