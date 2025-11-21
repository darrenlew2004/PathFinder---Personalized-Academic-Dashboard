import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableRow,
  TableCell,
} from '@mui/material';
import {
  TrendingUp,
  School,
  Person,
  CheckCircle,
  CalendarToday,
} from '@mui/icons-material';
import { AppDispatch, RootState } from '../../store';
import { fetchStudentStats } from '../../features/studentSlice';

const Dashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { currentStudent, loading, error } = useSelector((state: RootState) => state.students);

  useEffect(() => {
    // Only fetch if we don't already have student data from login
    if (!currentStudent) {
      dispatch(fetchStudentStats());
    }
  }, [dispatch, currentStudent]);

  if (loading && !currentStudent) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!currentStudent) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="info">No student data available</Alert>
      </Container>
    );
  }

  const getStatusColor = (status: string | undefined) => {
    if (!status) return 'default';
    const s = status.toLowerCase();
    if (s.includes('active') || s.includes('good')) return 'success';
    if (s.includes('probation') || s.includes('warning')) return 'warning';
    if (s.includes('graduated')) return 'info';
    return 'default';
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>
          Welcome back, {currentStudent.name || 'Student'}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Student ID: {currentStudent.id} | IC: {currentStudent.ic}
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Overall CGPA
                  </Typography>
                  <Typography variant="h4">
                    {currentStudent.overallcgpa?.toFixed(2) || 'N/A'}
                  </Typography>
                </Box>
                <TrendingUp color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Overall CAVG
                  </Typography>
                  <Typography variant="h4">
                    {currentStudent.overallcavg?.toFixed(2) || 'N/A'}
                  </Typography>
                </Box>
                <CheckCircle color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Current Year
                  </Typography>
                  <Typography variant="h4">{currentStudent.year || 'N/A'}</Typography>
                </Box>
                <School color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Semester
                  </Typography>
                  <Typography variant="h4">{currentStudent.sem || 'N/A'}</Typography>
                </Box>
                <CalendarToday color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Student Information */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                <Person sx={{ mr: 1 }} />
                Personal Information
              </Typography>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell><strong>Name</strong></TableCell>
                    <TableCell>{currentStudent.name || 'N/A'}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><strong>IC Number</strong></TableCell>
                    <TableCell>{currentStudent.ic || 'N/A'}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><strong>Gender</strong></TableCell>
                    <TableCell>{currentStudent.gender || 'N/A'}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><strong>Race</strong></TableCell>
                    <TableCell>{currentStudent.race || 'N/A'}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><strong>Country</strong></TableCell>
                    <TableCell>{currentStudent.country || 'N/A'}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><strong>Cohort</strong></TableCell>
                    <TableCell>{currentStudent.cohort || 'N/A'}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                <School sx={{ mr: 1 }} />
                Academic Information
              </Typography>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell><strong>Program</strong></TableCell>
                    <TableCell>{currentStudent.program || 'N/A'}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><strong>Program Code</strong></TableCell>
                    <TableCell>{currentStudent.programmecode || 'N/A'}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><strong>Year</strong></TableCell>
                    <TableCell>{currentStudent.year || 'N/A'}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><strong>Semester</strong></TableCell>
                    <TableCell>{currentStudent.sem || 'N/A'}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><strong>Status</strong></TableCell>
                    <TableCell>
                      <Chip 
                        label={currentStudent.status || 'Unknown'} 
                        color={getStatusColor(currentStudent.status)}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell><strong>Graduated</strong></TableCell>
                    <TableCell>
                      {currentStudent.graduated ? (
                        <Chip label="Yes" color="success" size="small" />
                      ) : (
                        <Chip label="No" color="default" size="small" />
                      )}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </Grid>

        {/* Academic Performance */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                <TrendingUp sx={{ mr: 1 }} />
                Academic Performance
              </Typography>
              <Grid container spacing={2} mt={1}>
                <Grid item xs={12} sm={4}>
                  <Box textAlign="center" p={2} bgcolor="primary.light" borderRadius={2}>
                    <Typography variant="body2" color="primary.contrastText">
                      Overall CGPA
                    </Typography>
                    <Typography variant="h3" color="primary.contrastText" fontWeight="bold">
                      {currentStudent.overallcgpa?.toFixed(2) || 'N/A'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box textAlign="center" p={2} bgcolor="success.light" borderRadius={2}>
                    <Typography variant="body2" color="success.contrastText">
                      Overall CAVG
                    </Typography>
                    <Typography variant="h3" color="success.contrastText" fontWeight="bold">
                      {currentStudent.overallcavg?.toFixed(2) || 'N/A'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Box textAlign="center" p={2} bgcolor="info.light" borderRadius={2}>
                    <Typography variant="body2" color="info.contrastText">
                      Year 1 CGPA
                    </Typography>
                    <Typography variant="h3" color="info.contrastText" fontWeight="bold">
                      {currentStudent.yearonecgpa?.toFixed(2) || 'N/A'}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;