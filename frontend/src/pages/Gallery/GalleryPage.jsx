import React from 'react';
import {
  Box,
  Button,
  Chip,
  Container,
  Grid,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import NorthEastIcon from '@mui/icons-material/NorthEast';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { useNavigate } from 'react-router-dom';

const showcaseProjects = [
  {
    title: 'Little Italy Restaurant Launch Kit',
    category: 'Menus, postcards, promo inserts',
    color: 'linear-gradient(135deg, #18212A 0%, #073B66 60%, #B64926 120%)',
    callout: 'Launch package',
    details: 'A coordinated opening-week print system that gives a neighborhood business a clean first impression across in-store and street-level touchpoints.',
    deliverables: ['Folded menus', 'Takeout inserts', 'Street postcards'],
  },
  {
    title: 'Broker Open House Collateral',
    category: 'Flyers, signage, listing leave-behinds',
    color: 'linear-gradient(135deg, #F2E9DE 0%, #FFFFFF 52%, #D36D47 130%)',
    callout: 'Sales enablement',
    details: 'Print pieces designed to hold up in fast-moving, last-minute event cycles while still feeling polished enough for premium listings.',
    deliverables: ['Window signage', 'Property handouts', 'Agent cards'],
  },
  {
    title: 'Boutique Retail Loyalty Campaign',
    category: 'Card decks, display cards, direct mail',
    color: 'linear-gradient(135deg, #10243A 0%, #28567B 52%, #F4EFE7 145%)',
    callout: 'Repeat business',
    details: 'A campaign system that mixes tactile in-store pieces with follow-up mailers for customers likely to return.',
    deliverables: ['Loyalty cards', 'Counter displays', 'Mailer cards'],
  },
];

const gallerySections = [
  {
    title: 'Brand systems for local businesses',
    body: 'Go Postal SD is strongest when a business needs more than a single item. The portfolio direction here emphasizes packages of work that operate together in the real world.',
  },
  {
    title: 'Print designed for use, not just display',
    body: 'The point of this gallery is to show output that survives customer hands, storefront counters, event tables, and shipping journeys without losing clarity or polish.',
  },
  {
    title: 'A place to prove trust visually',
    body: 'As real client-approved imagery is added, this page becomes a sales tool: less explanation, more proof of range, finish quality, and business fit.',
  },
];

const GalleryPage = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ py: { xs: 4, md: 7 }, position: 'relative', overflow: 'hidden' }}>
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(circle at top right, rgba(182,73,38,0.12), transparent 24%), radial-gradient(circle at bottom left, rgba(7,59,102,0.14), transparent 28%)',
          pointerEvents: 'none',
        }}
      />
      <Container maxWidth="lg">
        <Stack spacing={4}>
          <Paper
            elevation={0}
            sx={{
              p: { xs: 3, md: 5 },
              borderRadius: 6,
              border: '1px solid rgba(24,33,42,0.08)',
              background: 'linear-gradient(135deg, rgba(10,19,31,0.98), rgba(7,59,102,0.92) 58%, rgba(182,73,38,0.82) 130%)',
              color: 'white',
            }}
          >
            <Grid container spacing={4} alignItems="end">
              <Grid size={{ xs: 12, md: 8 }}>
                <Chip label="Portfolio" sx={{ mb: 2, backgroundColor: 'rgba(255,255,255,0.14)', color: 'white' }} />
                <Typography variant="h2" sx={{ fontSize: { xs: '2.4rem', md: '4rem' }, mb: 2 }}>
                  Work samples that look like the businesses they are made for.
                </Typography>
                <Typography variant="body1" sx={{ maxWidth: 760, lineHeight: 1.8, opacity: 0.92 }}>
                  Instead of a placeholder page talking about what a gallery could become, this version frames real showcase directions and makes the page feel like a visual proof surface for the kind of clients Go Postal SD is built to serve.
                </Typography>
              </Grid>
              <Grid size={{ xs: 12, md: 4 }}>
                <Stack spacing={2} alignItems={{ xs: 'flex-start', md: 'flex-end' }}>
                  <Button variant="contained" color="secondary" endIcon={<NorthEastIcon />} onClick={() => navigate('/contact')}>
                    Request a project consult
                  </Button>
                  <Button variant="outlined" sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.65)' }} onClick={() => navigate('/services')}>
                    View service approach
                  </Button>
                </Stack>
              </Grid>
            </Grid>
          </Paper>

          <Grid container spacing={3}>
            {showcaseProjects.map((project) => (
              <Grid size={{ xs: 12, lg: 4 }} key={project.title}>
                <Paper
                  elevation={0}
                  sx={{
                    borderRadius: 5,
                    overflow: 'hidden',
                    height: '100%',
                    border: '1px solid rgba(24,33,42,0.08)',
                    backgroundColor: 'background.paper',
                  }}
                >
                  <Box
                    sx={{
                      minHeight: 260,
                      p: 3,
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                      background: project.color,
                      color: project.color.includes('#F2E9DE') ? 'text.primary' : 'white',
                    }}
                  >
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
                      <Chip
                        label={project.callout}
                        icon={<AutoAwesomeIcon />}
                        sx={{
                          backgroundColor: 'rgba(255,255,255,0.16)',
                          color: 'inherit',
                          '& .MuiChip-icon': { color: 'inherit' },
                        }}
                      />
                      <Typography variant="overline" sx={{ opacity: 0.82 }}>
                        Showcase concept
                      </Typography>
                    </Stack>

                    <Box sx={{ ml: 'auto', mt: 4, width: '85%' }}>
                      <Paper sx={{ p: 2, borderRadius: 3, transform: 'rotate(-5deg)', backgroundColor: 'rgba(255,255,255,0.88)' }}>
                        <Typography variant="h5" sx={{ color: '#18212A' }}>
                          {project.category}
                        </Typography>
                      </Paper>
                    </Box>
                  </Box>

                  <Stack spacing={2} sx={{ p: 3.5 }}>
                    <Box>
                      <Typography variant="h5" fontWeight={700} gutterBottom>
                        {project.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.8 }}>
                        {project.details}
                      </Typography>
                    </Box>
                    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                      {project.deliverables.map((deliverable) => (
                        <Chip key={deliverable} label={deliverable} variant="outlined" />
                      ))}
                    </Stack>
                  </Stack>
                </Paper>
              </Grid>
            ))}
          </Grid>

          <Grid container spacing={3}>
            {gallerySections.map((section, index) => (
              <Grid size={{ xs: 12, md: 4 }} key={section.title}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 3.5,
                    borderRadius: 5,
                    height: '100%',
                    border: '1px solid rgba(24,33,42,0.08)',
                    background: index === 1 ? 'linear-gradient(180deg, rgba(182,73,38,0.06), rgba(255,255,255,0.92))' : 'linear-gradient(180deg, rgba(7,59,102,0.05), rgba(255,255,255,0.94))',
                  }}
                >
                  <Typography variant="overline" color="text.secondary">
                    Why it matters
                  </Typography>
                  <Typography variant="h5" fontWeight={700} sx={{ my: 1.5 }}>
                    {section.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.8 }}>
                    {section.body}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Stack>
      </Container>
    </Box>
  );
};

export default GalleryPage;
