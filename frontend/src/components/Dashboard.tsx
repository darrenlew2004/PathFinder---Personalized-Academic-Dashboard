import React, { useEffect, useState } from 'react';
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
  Tabs,
  Tab,
  TableHead,
  TableContainer,
  Paper,
  LinearProgress,
  Tooltip,
  Collapse,
  IconButton,
} from '@mui/material';
import {
  TrendingUp,
  School,
  Person,
  CheckCircle,
  CalendarToday,
  BookOutlined,
  Analytics,
  ExpandMore,
  ExpandLess,
  Warning,
  Info,
} from '@mui/icons-material';
import { AppDispatch, RootState } from '../../store';
import { fetchStudentStats, fetchStudentWithSubjects } from '../../features/studentSlice';
import { listVariants, whatIf, VariantsResponse, ProgressResponse, WhatIfResponse, getStudentProgress } from '../../services/catalogue';
import { getStudentAnalytics, StudentProfile } from '../../services/analytics';
import { getMultipleSubjectPredictions, StudentPredictionReport, SubjectPrediction, getRiskColor, getRiskEmoji, formatProbability } from '../../services/predictions';

const Dashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { currentStudent, studentWithSubjects, loading, error } = useSelector((state: RootState) => state.students);
  const [tabValue, setTabValue] = useState(0);
  // Planner state
  const [variants, setVariants] = useState<string[]>([]);
  const [selectedVariant, setSelectedVariant] = useState<string>('202301-normal');
  const [progress, setProgress] = useState<ProgressResponse | null>(null);
  const [whatIfResult, setWhatIfResult] = useState<WhatIfResponse | null>(null);
  const [plannerLoading, setPlannerLoading] = useState(false);
  const [plannerError, setPlannerError] = useState<string | null>(null);
  // Analytics state
  const [analyticsData, setAnalyticsData] = useState<StudentProfile | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsError, setAnalyticsError] = useState<string | null>(null);
  // Predictions state
  const [predictions, setPredictions] = useState<StudentPredictionReport | null>(null);
  const [predictionsLoading, setPredictionsLoading] = useState(false);
  const [expandedPrediction, setExpandedPrediction] = useState<string | null>(null);

  useEffect(() => {
    // Only fetch if we don't already have student data from login
    if (!currentStudent) {
      dispatch(fetchStudentStats());
    }
  }, [dispatch, currentStudent]);

  useEffect(() => {
    // Fetch subjects when switching to Courses tab
    if (tabValue === 1 && currentStudent && !studentWithSubjects) {
      dispatch(fetchStudentWithSubjects(currentStudent.id));
    }
    // Load planner data when switching to Planner tab
    if (tabValue === 2 && !progress) {
      (async () => {
        try {
          setPlannerError(null);
          setPlannerLoading(true);
          
          // Ensure we have subjects available for what-if derivation
          if (currentStudent && !studentWithSubjects) {
            dispatch(fetchStudentWithSubjects(currentStudent.id));
          }
          
          // Fetch variants and progress in parallel
          const [v, prog] = await Promise.all([
            listVariants(),
            getStudentProgress(selectedVariant.split('-')[0] || '202301', selectedVariant.split('-')[1] || 'normal')
          ]);
          
          setVariants(v.variants);
          const key = selectedVariant && v.variants.includes(selectedVariant) ? selectedVariant : v.variants[0];
          setSelectedVariant(key);
          setProgress(prog);
          
          // Fetch what-if in background (don't block UI)
          const intake = key.split('-')[0];
          const entry = key.split('-')[1];
          whatIf({
            intake,
            entry_type: entry,
            planned_codes: ['PRG1203','SEG1201','NET1014'],
            completed_codes: (studentWithSubjects?.subjects || [])
              .filter(s => s.grade && !['F','FA','W'].includes(String(s.grade).toUpperCase()))
              .map(s => s.subjectcode || '')
              .filter(Boolean),
            cgpa: currentStudent?.overallcgpa ?? 3.0,
            attendance: 90,
            gpa_trend: 0.0,
          }).then(setWhatIfResult).catch(console.error);
          
        } catch (e: any) {
          setPlannerError(e?.message || 'Failed to load planner');
        } finally {
          setPlannerLoading(false);
        }
      })();
    }
  }, [tabValue, currentStudent, studentWithSubjects, dispatch, progress]);

  // Recompute planner data on variant change while Planner is active
  useEffect(() => {
    if (tabValue !== 2 || !progress) return;
    // Only re-fetch if variant actually changed and we have initial data
    const intake = selectedVariant.split('-')[0];
    const entry = selectedVariant.split('-')[1];
    if (!intake || !entry) return;
    
    (async () => {
      try {
        setPlannerLoading(true);
        // Fetch progress and what-if in parallel
        const [prog, wi] = await Promise.all([
          getStudentProgress(intake, entry),
          whatIf({
            intake,
            entry_type: entry,
            planned_codes: ['PRG1203','SEG1201','NET1014'],
            completed_codes: (studentWithSubjects?.subjects || [])
              .filter(s => s.grade && !['F','FA','W'].includes(String(s.grade).toUpperCase()))
              .map(s => s.subjectcode || '')
              .filter(Boolean),
            cgpa: currentStudent?.overallcgpa ?? 3.0,
            attendance: 90,
            gpa_trend: 0.0,
          })
        ]);
        setProgress(prog);
        setWhatIfResult(wi);
        // Reset predictions when variant changes so they reload
        setPredictions(null);
      } catch (e: any) {
        setPlannerError(e?.message || 'Failed to compute planner');
      } finally {
        setPlannerLoading(false);
      }
    })();
  }, [selectedVariant]);

  // Load subject predictions when planner tab is active and we have progress data
  useEffect(() => {
    if (tabValue === 2 && currentStudent && progress && !predictions && !predictionsLoading) {
      (async () => {
        try {
          setPredictionsLoading(true);
          // Get predictions for remaining core subjects
          const subjectCodes = progress.core_remaining.slice(0, 10); // Limit to 10 for performance
          if (subjectCodes.length > 0) {
            const report = await getMultipleSubjectPredictions(currentStudent.id, subjectCodes);
            setPredictions(report);
          }
        } catch (e: any) {
          console.error('Failed to load predictions:', e);
        } finally {
          setPredictionsLoading(false);
        }
      })();
    }
  }, [tabValue, currentStudent, progress, predictions, predictionsLoading]);

  // Load analytics data when switching to Analytics tab
  useEffect(() => {
    if (tabValue === 3 && currentStudent && !analyticsData) {
      (async () => {
        try {
          setAnalyticsLoading(true);
          setAnalyticsError(null);
          const data = await getStudentAnalytics(currentStudent.id);
          setAnalyticsData(data);
        } catch (e: any) {
          setAnalyticsError(e?.message || 'Failed to load analytics');
        } finally {
          setAnalyticsLoading(false);
        }
      })();
    }
  }, [tabValue, currentStudent, analyticsData]);

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

  const getGradeColor = (grade: string | undefined) => {
    if (!grade) return 'default';
    const g = grade.toUpperCase();
    if (['A', 'A+', 'A-'].includes(g)) return 'success';
    if (['B', 'B+', 'B-'].includes(g)) return 'info';
    if (['C', 'C+', 'C-'].includes(g)) return 'warning';
    if (['D', 'E', 'F'].includes(g)) return 'error';
    return 'default';
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
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

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Overview" icon={<School />} iconPosition="start" />
          <Tab label="Courses" icon={<BookOutlined />} iconPosition="start" />
          <Tab label="Planner" icon={<TrendingUp />} iconPosition="start" />
          <Tab label="Analytics" icon={<Analytics />} iconPosition="start" />
        </Tabs>
      </Box>

      {/* Overview Tab */}
      {tabValue === 0 && (
        <>
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
        </>
      )}

      {/* Courses Tab */}
      {tabValue === 1 && (
        <>
          {loading ? (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert severity="error">{error}</Alert>
          ) : !studentWithSubjects || !studentWithSubjects.subjects.length ? (
            <Alert severity="info">No course data available</Alert>
          ) : (
            <>
              {/* Course Statistics Summary */}
              <Grid container spacing={3} mb={4}>
                <Grid item xs={12} sm={6} md={3}>
                  <Card>
                    <CardContent>
                      <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Box>
                          <Typography color="text.secondary" gutterBottom variant="body2">
                            Total Courses
                          </Typography>
                          <Typography variant="h4">
                            {studentWithSubjects.total_subjects}
                          </Typography>
                        </Box>
                        <BookOutlined color="primary" sx={{ fontSize: 40 }} />
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
                            Avg Attendance
                          </Typography>
                          <Typography variant="h4">
                            {studentWithSubjects.average_attendance?.toFixed(1) || 'N/A'}%
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
                            Avg Overall %
                          </Typography>
                          <Typography variant="h4">
                            {studentWithSubjects.average_percentage?.toFixed(1) || 'N/A'}%
                          </Typography>
                        </Box>
                        <TrendingUp color="info" sx={{ fontSize: 40 }} />
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
                            Status
                          </Typography>
                          <Chip 
                            label={currentStudent.status || 'Unknown'} 
                            color={getStatusColor(currentStudent.status)}
                            size="small"
                          />
                        </Box>
                        <Person color="warning" sx={{ fontSize: 40 }} />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* Courses Table */}
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                    <BookOutlined sx={{ mr: 1 }} />
                    Course Performance Details
                  </Typography>
                  <TableContainer component={Paper} sx={{ mt: 2 }}>
                    <Table>
                      <TableHead>
                        <TableRow sx={{ bgcolor: 'primary.main' }}>
                          <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Code</TableCell>
                          <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Course Name</TableCell>
                          <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">Grade</TableCell>
                          <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">Overall %</TableCell>
                          <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">Attendance %</TableCell>
                          <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">Coursework %</TableCell>
                          <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">Year/Month</TableCell>
                          <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">Status</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {studentWithSubjects.subjects.map((subject) => (
                          <TableRow key={subject.id} hover>
                            <TableCell>
                              <Typography variant="body2" fontWeight="medium">
                                {subject.subjectcode || 'N/A'}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2">
                                {subject.subjectname || 'N/A'}
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              {subject.grade ? (
                                <Chip 
                                  label={subject.grade} 
                                  color={getGradeColor(subject.grade)}
                                  size="small"
                                />
                              ) : 'N/A'}
                            </TableCell>
                            <TableCell align="center">
                              <Box>
                                <Typography variant="body2">
                                  {subject.overallpercentage?.toFixed(1) || 'N/A'}
                                  {subject.overallpercentage && '%'}
                                </Typography>
                                {subject.overallpercentage && (
                                  <LinearProgress 
                                    variant="determinate" 
                                    value={subject.overallpercentage} 
                                    sx={{ mt: 0.5, height: 6, borderRadius: 1 }}
                                    color={
                                      subject.overallpercentage >= 70 ? 'success' :
                                      subject.overallpercentage >= 50 ? 'warning' : 'error'
                                    }
                                  />
                                )}
                              </Box>
                            </TableCell>
                            <TableCell align="center">
                              <Box>
                                <Typography variant="body2">
                                  {subject.attendancepercentage?.toFixed(1) || 'N/A'}
                                  {subject.attendancepercentage && '%'}
                                </Typography>
                                {subject.attendancepercentage && (
                                  <LinearProgress 
                                    variant="determinate" 
                                    value={subject.attendancepercentage} 
                                    sx={{ mt: 0.5, height: 6, borderRadius: 1 }}
                                    color={
                                      subject.attendancepercentage >= 80 ? 'success' :
                                      subject.attendancepercentage >= 60 ? 'warning' : 'error'
                                    }
                                  />
                                )}
                              </Box>
                            </TableCell>
                            <TableCell align="center">
                              {subject.courseworkpercentage?.toFixed(1) || 'N/A'}
                              {subject.courseworkpercentage && '%'}
                            </TableCell>
                            <TableCell align="center">
                              {subject.examyear && subject.exammonth 
                                ? `${subject.examyear}/${subject.exammonth}` 
                                : 'N/A'}
                            </TableCell>
                            <TableCell align="center">
                              {subject.status || 'N/A'}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </>
          )}
        </>
      )}

      {/* Planner Tab */}
      {tabValue === 2 && (
        <>
          {plannerLoading ? (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
              <CircularProgress />
            </Box>
          ) : plannerError ? (
            <Alert severity="error">{plannerError}</Alert>
          ) : (
            <>
              <Grid container spacing={3} mb={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Programme Variants
                      </Typography>
                      <Box>
                        <Typography variant="body2" color="text.secondary">Select a variant:</Typography>
                        <select
                          value={selectedVariant}
                          onChange={(e) => setSelectedVariant(e.target.value)}
                          style={{ padding: '8px', marginTop: '8px', width: '100%' }}
                        >
                          {variants.map((v) => (
                            <option key={v} value={v}>{v}</option>
                          ))}
                        </select>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Progress Summary
                      </Typography>
                      {progress ? (
                        <Box>
                          <Typography>Completed Credits: {progress.completed_credits}</Typography>
                          <Typography>Total Credits: {progress.total_credits}</Typography>
                          <Typography>Percent Complete: {progress.percent_complete}%</Typography>
                          <Box mt={1}>
                            <LinearProgress variant="determinate" value={progress.percent_complete} />
                          </Box>
                        </Box>
                      ) : (
                        <Typography color="text.secondary">No progress data</Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Outstanding Requirements
                      </Typography>
                      {progress ? (
                        <Box>
                          <Typography variant="body2" color="text.secondary">Core Remaining ({progress.core_remaining.length})</Typography>
                          <Box sx={{ maxHeight: 180, overflowY: 'auto', border: '1px solid #eee', p: 1, borderRadius: 1 }}>
                            {progress.core_remaining.map((c) => (
                              <Chip key={c} label={c} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                            ))}
                          </Box>
                          <Typography variant="body2" color="text.secondary" mt={2}>Discipline Elective Slots</Typography>
                          <Box>
                            {progress.discipline_elective_placeholders_remaining.map((c) => (
                              <Chip key={c} label={c} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                            ))}
                          </Box>
                          <Typography variant="body2" color="text.secondary" mt={2}>Free Elective Slots</Typography>
                          <Box>
                            {progress.free_elective_placeholders_remaining.map((c) => (
                              <Chip key={c} label={c} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                            ))}
                          </Box>
                          <Typography variant="body2" color="text.secondary" mt={2}>Either-Subject Pairs</Typography>
                          <Box>
                            {progress.either_pairs_remaining.map((pair, idx) => (
                              <Chip key={idx} label={`${pair[0]} / ${pair[1]}`} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                            ))}
                          </Box>
                        </Box>
                      ) : (
                        <Typography color="text.secondary">No outstanding data</Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        What-If Risk (Sample Plan)
                      </Typography>
                      {whatIfResult ? (
                        <Box>
                          <Typography>Total Credits: {whatIfResult.total_credits}</Typography>
                          <Typography>Aggregate Risk: {whatIfResult.risk_band} ({whatIfResult.aggregated_risk_score})</Typography>
                          <Box mt={1}>
                            {whatIfResult.per_course.map((c) => (
                              <Box key={c.subject_code} display="flex" alignItems="center" justifyContent="space-between" py={0.5}>
                                <Typography>{c.subject_code} - {c.subject_name}</Typography>
                                <Chip label={c.predicted_risk} color={c.predicted_risk === 'low' ? 'success' : c.predicted_risk === 'medium' ? 'warning' : 'error'} size="small" />
                              </Box>
                            ))}
                          </Box>
                        </Box>
                      ) : (
                        <Typography color="text.secondary">No what-if data</Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* Subject Success Predictions */}
              <Card sx={{ mt: 3 }}>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={1} mb={2}>
                    <Warning color="warning" />
                    <Typography variant="h6">
                      Subject Success Predictions
                    </Typography>
                    <Tooltip title="Predictions based on your performance in prerequisite subjects">
                      <Info fontSize="small" color="action" />
                    </Tooltip>
                  </Box>
                  
                  {predictionsLoading ? (
                    <Box display="flex" justifyContent="center" py={2}>
                      <CircularProgress size={24} />
                    </Box>
                  ) : predictions && predictions.predictions.length > 0 ? (
                    <>
                      {predictions.high_risk_subjects.length > 0 && (
                        <Alert severity="warning" sx={{ mb: 2 }}>
                          <strong>Attention needed:</strong> {predictions.high_risk_subjects.length} subject(s) may be challenging based on your prerequisite performance.
                        </Alert>
                      )}
                      
                      <TableContainer component={Paper} variant="outlined">
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Subject</TableCell>
                              <TableCell align="center">Risk Level</TableCell>
                              <TableCell align="center">Success Probability</TableCell>
                              <TableCell align="center">Prereq GPA</TableCell>
                              <TableCell></TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {predictions.predictions.map((pred: SubjectPrediction) => (
                              <React.Fragment key={pred.subject_code}>
                                <TableRow 
                                  sx={{ 
                                    '&:hover': { bgcolor: 'action.hover' },
                                    cursor: 'pointer',
                                    bgcolor: pred.risk_level === 'high' || pred.risk_level === 'very_high' 
                                      ? 'error.lighter' 
                                      : undefined
                                  }}
                                  onClick={() => setExpandedPrediction(
                                    expandedPrediction === pred.subject_code ? null : pred.subject_code
                                  )}
                                >
                                  <TableCell>
                                    <Box>
                                      <Typography variant="body2" fontWeight="medium">
                                        {pred.subject_code}
                                      </Typography>
                                      <Typography variant="caption" color="text.secondary">
                                        {pred.subject_name}
                                      </Typography>
                                    </Box>
                                  </TableCell>
                                  <TableCell align="center">
                                    <Chip 
                                      label={`${getRiskEmoji(pred.risk_level)} ${pred.risk_level.replace('_', ' ')}`}
                                      color={getRiskColor(pred.risk_level)}
                                      size="small"
                                    />
                                  </TableCell>
                                  <TableCell align="center">
                                    <Typography 
                                      fontWeight="bold"
                                      color={pred.predicted_success_probability >= 0.8 ? 'success.main' : 
                                             pred.predicted_success_probability >= 0.6 ? 'warning.main' : 'error.main'}
                                    >
                                      {formatProbability(pred.predicted_success_probability)}
                                    </Typography>
                                  </TableCell>
                                  <TableCell align="center">
                                    <Typography variant="body2">
                                      {pred.weighted_prereq_gpa > 0 ? pred.weighted_prereq_gpa.toFixed(2) : 'N/A'}
                                    </Typography>
                                  </TableCell>
                                  <TableCell>
                                    <IconButton size="small">
                                      {expandedPrediction === pred.subject_code ? <ExpandLess /> : <ExpandMore />}
                                    </IconButton>
                                  </TableCell>
                                </TableRow>
                                <TableRow>
                                  <TableCell colSpan={5} sx={{ py: 0, borderBottom: 'none' }}>
                                    <Collapse in={expandedPrediction === pred.subject_code} timeout="auto" unmountOnExit>
                                      <Box sx={{ py: 2, px: 1, bgcolor: 'grey.50', borderRadius: 1, my: 1 }}>
                                        <Typography variant="body2" paragraph>
                                          {pred.recommendation}
                                        </Typography>
                                        
                                        {pred.prereq_performance.length > 0 && (
                                          <Box mb={2}>
                                            <Typography variant="caption" fontWeight="bold" color="text.secondary">
                                              Prerequisite Performance:
                                            </Typography>
                                            <Box display="flex" flexWrap="wrap" gap={1} mt={0.5}>
                                              {pred.prereq_performance.map((p) => (
                                                <Chip
                                                  key={p.subject_code}
                                                  label={`${p.subject_code}: ${p.grade}`}
                                                  size="small"
                                                  color={p.grade_points >= 3.0 ? 'success' : 
                                                         p.grade_points >= 2.0 ? 'warning' : 'error'}
                                                  variant="outlined"
                                                />
                                              ))}
                                            </Box>
                                          </Box>
                                        )}
                                        
                                        {pred.missing_prereqs.length > 0 && (
                                          <Box>
                                            <Typography variant="caption" fontWeight="bold" color="text.secondary">
                                              Missing Prerequisites:
                                            </Typography>
                                            <Box display="flex" flexWrap="wrap" gap={1} mt={0.5}>
                                              {pred.missing_prereqs.map((code) => (
                                                <Chip
                                                  key={code}
                                                  label={code}
                                                  size="small"
                                                  color="default"
                                                  variant="outlined"
                                                />
                                              ))}
                                            </Box>
                                          </Box>
                                        )}
                                        
                                        {pred.cohort_pass_rate !== null && (
                                          <Box mt={2}>
                                            <Typography variant="caption" color="text.secondary">
                                              Cohort pass rate: {(pred.cohort_pass_rate * 100).toFixed(0)}% | 
                                              Avg score: {pred.cohort_avg_score?.toFixed(1) || 'N/A'}%
                                            </Typography>
                                          </Box>
                                        )}
                                      </Box>
                                    </Collapse>
                                  </TableCell>
                                </TableRow>
                              </React.Fragment>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                      
                      {predictions.recommended_order.length > 0 && (
                        <Box mt={2}>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            <strong>Recommended order</strong> (lower risk first):
                          </Typography>
                          <Box display="flex" flexWrap="wrap" gap={0.5}>
                            {predictions.recommended_order.map((code, idx) => (
                              <Chip 
                                key={code} 
                                label={`${idx + 1}. ${code}`} 
                                size="small" 
                                variant="outlined"
                              />
                            ))}
                          </Box>
                        </Box>
                      )}
                    </>
                  ) : (
                    <Typography color="text.secondary">
                      No prediction data available. Complete some prerequisite subjects first.
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </>
          )}
        </>
      )}

      {/* Analytics Tab */}
      {tabValue === 3 && (
        <>
          {analyticsLoading ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : analyticsError ? (
            <Alert severity="error">{analyticsError}</Alert>
          ) : analyticsData ? (
            <>
              {/* Key Metrics */}
              <Grid container spacing={3} mb={4}>
                <Grid item xs={12} sm={6} md={3}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" variant="body2" gutterBottom>
                        Current GPA
                      </Typography>
                      <Typography variant="h4">
                        {analyticsData.current_gpa?.toFixed(2) || 'N/A'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        out of 4.0
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" variant="body2" gutterBottom>
                        Average Score
                      </Typography>
                      <Typography variant="h4">
                        {analyticsData.avg_score?.toFixed(1) || 'N/A'}%
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        ± {analyticsData.score_std?.toFixed(1) || '0'} std dev
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" variant="body2" gutterBottom>
                        Subjects Taken
                      </Typography>
                      <Typography variant="h4">
                        {analyticsData.subjects_taken}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        across {analyticsData.terms_taken} terms
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Card>
                    <CardContent>
                      <Typography color="text.secondary" variant="body2" gutterBottom>
                        Score Trend
                      </Typography>
                      <Typography variant="h4" color={analyticsData.score_trend_per_term && analyticsData.score_trend_per_term > 0 ? 'success.main' : analyticsData.score_trend_per_term && analyticsData.score_trend_per_term < 0 ? 'error.main' : 'text.primary'}>
                        {analyticsData.score_trend_per_term ? (analyticsData.score_trend_per_term > 0 ? '+' : '') + analyticsData.score_trend_per_term.toFixed(1) : 'N/A'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        % per term
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* Best/Worst Subjects & Benchmark */}
              <Grid container spacing={3} mb={4}>
                <Grid item xs={12} md={4}>
                  <Card sx={{ height: '100%', borderLeft: 4, borderColor: 'success.main' }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom color="success.main">
                        Best Subject
                      </Typography>
                      {analyticsData.best_subject ? (
                        <>
                          <Typography variant="body1" fontWeight="bold">
                            {analyticsData.best_subject.subjectname}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {analyticsData.best_subject.subjectcode}
                          </Typography>
                          <Typography variant="h5" mt={1}>
                            {analyticsData.best_subject.overallpercentage?.toFixed(1)}%
                          </Typography>
                        </>
                      ) : (
                        <Typography color="text.secondary">No data</Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card sx={{ height: '100%', borderLeft: 4, borderColor: 'error.main' }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom color="error.main">
                        Needs Improvement
                      </Typography>
                      {analyticsData.worst_subject ? (
                        <>
                          <Typography variant="body1" fontWeight="bold">
                            {analyticsData.worst_subject.subjectname}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {analyticsData.worst_subject.subjectcode}
                          </Typography>
                          <Typography variant="h5" mt={1}>
                            {analyticsData.worst_subject.overallpercentage?.toFixed(1)}%
                          </Typography>
                        </>
                      ) : (
                        <Typography color="text.secondary">No data</Typography>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Performance Summary
                      </Typography>
                      <Table size="small">
                        <TableBody>
                          <TableRow>
                            <TableCell>Benchmark Delta</TableCell>
                            <TableCell align="right">
                              <Chip 
                                label={analyticsData.avg_benchmark_delta ? (analyticsData.avg_benchmark_delta > 0 ? '+' : '') + analyticsData.avg_benchmark_delta.toFixed(1) + '%' : 'N/A'} 
                                color={analyticsData.avg_benchmark_delta && analyticsData.avg_benchmark_delta > 0 ? 'success' : analyticsData.avg_benchmark_delta && analyticsData.avg_benchmark_delta < 0 ? 'error' : 'default'}
                                size="small"
                              />
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Failed Subjects</TableCell>
                            <TableCell align="right">
                              <Chip label={analyticsData.fails_count} color={analyticsData.fails_count > 0 ? 'error' : 'success'} size="small" />
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Retakes</TableCell>
                            <TableCell align="right">
                              <Chip label={analyticsData.retakes_count} color={analyticsData.retakes_count > 0 ? 'warning' : 'default'} size="small" />
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* Term Performance Timeline */}
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Performance by Term
                  </Typography>
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Term</TableCell>
                          <TableCell align="right">Avg Score</TableCell>
                          <TableCell align="right">Exams</TableCell>
                          <TableCell align="right">Pass Rate</TableCell>
                          <TableCell>Progress</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {analyticsData.term_stats.map((term) => (
                          <TableRow key={term.term}>
                            <TableCell>{term.term}</TableCell>
                            <TableCell align="right">
                              {term.avg_percentage?.toFixed(1) || 'N/A'}%
                            </TableCell>
                            <TableCell align="right">{term.total_exams}</TableCell>
                            <TableCell align="right">
                              <Chip 
                                label={`${term.pass_rate?.toFixed(0) || 0}%`} 
                                color={term.pass_rate && term.pass_rate >= 80 ? 'success' : term.pass_rate && term.pass_rate >= 50 ? 'warning' : 'error'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell sx={{ width: '30%' }}>
                              <LinearProgress 
                                variant="determinate" 
                                value={term.avg_percentage || 0}
                                color={term.avg_percentage && term.avg_percentage >= 60 ? 'success' : term.avg_percentage && term.avg_percentage >= 40 ? 'warning' : 'error'}
                                sx={{ height: 8, borderRadius: 4 }}
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </CardContent>
              </Card>
            </>
          ) : (
            <Alert severity="info">No analytics data available</Alert>
          )}
        </>
      )}
    </Container>
  );
};

export default Dashboard;