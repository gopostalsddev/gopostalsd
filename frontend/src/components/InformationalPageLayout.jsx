import React from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Container,
  Grid,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

const InformationalPageLayout = ({
  eyebrow,
  title,
  subtitle,
  highlights = [],
  sections = [],
  metrics = [],
  primaryAction,
  secondaryAction,
}) => {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        py: { xs: 4, md: 7 },
        backgroundColor: 'transparent',
        minHeight: '100%',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          inset: 0,
          background:
            'linear-gradient(180deg, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0) 24%), repeating-linear-gradient(135deg, rgba(24,33,42,0.025) 0px, rgba(24,33,42,0.025) 1px, transparent 1px, transparent 18px)',
          pointerEvents: 'none',
        }}
      />
      <Container maxWidth="lg">
        <Stack spacing={4}>
          <Paper
            elevation={3}
            sx={{
              p: { xs: 3, md: 5 },
              borderRadius: 6,
              position: 'relative',
              overflow: 'hidden',
              background:
                'linear-gradient(135deg, rgba(10, 19, 31, 0.98), rgba(7, 59, 102, 0.92) 58%, rgba(182, 73, 38, 0.82) 130%)',
              color: 'white',
              '&::before': {
                content: '""',
                position: 'absolute',
                right: -120,
                top: -80,
                width: 280,
                height: 280,
                borderRadius: '50%',
                background: 'radial-gradient(circle, rgba(255,255,255,0.18) 0%, rgba(255,255,255,0) 68%)',
              },
            }}
          >
            <Stack spacing={3} sx={{ position: 'relative' }}>
              {eyebrow && (
                <Chip
                  label={eyebrow}
                  sx={{
                    alignSelf: 'flex-start',
                    backgroundColor: 'rgba(255,255,255,0.14)',
                    color: 'white',
                    border: '1px solid rgba(255,255,255,0.18)',
                  }}
                />
              )}
              <Grid container spacing={4} alignItems="flex-end">
                <Grid size={{ xs: 12, md: 8 }}>
                  <Stack spacing={2.5}>
                    <Typography variant="h2" fontWeight={700} sx={{ maxWidth: 820, fontSize: { xs: '2.4rem', md: '4rem' } }}>
                      {title}
                    </Typography>
                    <Typography variant="body1" sx={{ maxWidth: 760, opacity: 0.92, fontSize: '1.05rem', lineHeight: 1.8 }}>
                      {subtitle}
                    </Typography>
                    {(primaryAction || secondaryAction) && (
                      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                        {primaryAction && (
                          <Button variant="contained" color="secondary" onClick={() => navigate(primaryAction.to)}>
                            {primaryAction.label}
                          </Button>
                        )}
                        {secondaryAction && (
                          <Button
                            variant="outlined"
                            onClick={() => navigate(secondaryAction.to)}
                            sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.65)' }}
                          >
                            {secondaryAction.label}
                          </Button>
                        )}
                      </Stack>
                    )}
                  </Stack>
                </Grid>
                <Grid size={{ xs: 12, md: 4 }}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      borderRadius: 4,
                      backgroundColor: 'rgba(255,255,255,0.1)',
                      border: '1px solid rgba(255,255,255,0.15)',
                      backdropFilter: 'blur(10px)',
                    }}
                  >
                    <Typography variant="overline" sx={{ opacity: 0.7 }}>
                      Brand promise
                    </Typography>
                    <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>
                      Practical print expertise, local accountability, faster follow-through.
                    </Typography>
                    <Typography variant="body2" sx={{ opacity: 0.86, lineHeight: 1.75 }}>
                      These pages are designed to feel like a storefront with an informed team behind it, not just a product catalog.
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </Stack>
          </Paper>

          {metrics.length > 0 && (
            <Grid container spacing={3}>
              {metrics.map((metric) => (
                <Grid size={{ xs: 12, sm: 6, md: 3 }} key={metric.label}>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 3,
                      borderRadius: 4,
                      height: '100%',
                      border: '1px solid rgba(24, 33, 42, 0.08)',
                      background: 'linear-gradient(180deg, rgba(255,255,255,0.82), rgba(255,255,255,0.6))',
                      backdropFilter: 'blur(6px)',
                    }}
                  >
                    <Typography variant="overline" color="text.secondary">
                      {metric.label}
                    </Typography>
                    <Typography variant="h4" fontWeight={700} sx={{ my: 1 }}>
                      {metric.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {metric.caption}
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          )}

          {highlights.length > 0 && (
            <Grid container spacing={3}>
              {highlights.map((highlight, index) => (
                <Grid size={{ xs: 12, md: 4 }} key={highlight.title}>
                  <Card
                    elevation={0}
                    sx={{
                      borderRadius: 5,
                      height: '100%',
                      border: '1px solid rgba(24, 33, 42, 0.08)',
                      background:
                        index === 1
                          ? 'linear-gradient(180deg, rgba(182,73,38,0.08), rgba(255,255,255,0.92))'
                          : 'linear-gradient(180deg, rgba(7,59,102,0.06), rgba(255,255,255,0.92))',
                    }}
                  >
                    <CardContent sx={{ p: 3.5 }}>
                      <Typography variant="overline" color="text.secondary">
                        Signature capability
                      </Typography>
                      <Typography variant="h5" fontWeight={700} gutterBottom>
                        {highlight.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.8 }}>
                        {highlight.description}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}

          <Grid container spacing={3}>
            {sections.map((section, index) => (
              <Grid size={{ xs: 12, md: section.fullWidth ? 12 : 6 }} key={section.heading}>
                <Paper
                  elevation={0}
                  sx={{
                    p: { xs: 3, md: 4 },
                    borderRadius: 5,
                    height: '100%',
                    border: '1px solid rgba(24, 33, 42, 0.08)',
                    background:
                      index % 2 === 0
                        ? 'linear-gradient(180deg, rgba(255,255,255,0.88), rgba(255,255,255,0.74))'
                        : 'linear-gradient(180deg, rgba(248,242,234,0.96), rgba(255,255,255,0.9))',
                  }}
                >
                  <Stack spacing={2.2}>
                    <Typography variant="overline" color="text.secondary">
                      {section.fullWidth ? 'Reference' : 'Focus area'}
                    </Typography>
                    <Typography variant="h4" fontWeight={700} sx={{ fontSize: { xs: '1.55rem', md: '1.9rem' } }}>
                      {section.heading}
                    </Typography>
                    {section.body && (
                      <Typography variant="body1" color="text.secondary" sx={{ lineHeight: 1.8 }}>
                        {section.body}
                      </Typography>
                    )}
                    {section.bullets?.map((bullet) => (
                      <Stack key={bullet} direction="row" spacing={1.5} alignItems="flex-start">
                        <Box
                          sx={{
                            width: 10,
                            height: 10,
                            mt: '8px',
                            borderRadius: '50%',
                            background: 'linear-gradient(135deg, #B64926, #073B66)',
                            flexShrink: 0,
                          }}
                        />
                        <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.75 }}>
                          {bullet}
                        </Typography>
                      </Stack>
                    ))}
                  </Stack>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Stack>
      </Container>
    </Box>
  );
};

export default InformationalPageLayout;
