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
} from '@mui/material';
import {
  TrendingUp,
  School,
  Person,
  CheckCircle,
  CalendarToday,
  BookOutlined,
} from '@mui/icons-material';
import { AppDispatch, RootState } from '../../store';
import { fetchStudentStats, fetchStudentWithSubjects } from '../../features/studentSlice';
import { listVariants, computeProgress, whatIf, getElectives, VariantsResponse, ProgressResponse, WhatIfResponse, getStudentProgress } from '../../services/catalogue';

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
    if (tabValue === 2) {
      (async () => {
        try {
          setPlannerError(null);
          setPlannerLoading(true);
          const v: VariantsResponse = await listVariants();
          setVariants(v.variants);
          const key = selectedVariant && v.variants.includes(selectedVariant) ? selectedVariant : v.variants[0];
          setSelectedVariant(key);
          const intake = key.split('-')[0];
          const entry = key.split('-')[1];
          // Ensure we have subjects available for what-if derivation
          if (currentStudent && !studentWithSubjects) {
            dispatch(fetchStudentWithSubjects(currentStudent.id));
          }
          // Use server-side student progress
          const prog = await getStudentProgress(intake, entry);
          setProgress(prog);
          const wi = await whatIf({
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
          });
          setWhatIfResult(wi);
        } catch (e: any) {
          setPlannerError(e?.message || 'Failed to load planner');
        } finally {
          setPlannerLoading(false);
        }
      })();
    }
  }, [tabValue, currentStudent, studentWithSubjects, dispatch]);

  // Recompute planner data on variant change while Planner is active
  useEffect(() => {
    if (tabValue !== 2) return;
    (async () => {
      try {
        setPlannerError(null);
        setPlannerLoading(true);
        const key = selectedVariant;
        if (!key) return;
        const intake = key.split('-')[0];
        const entry = key.split('-')[1];
        const prog = await getStudentProgress(intake, entry);
        setProgress(prog);
        const wi = await whatIf({
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
        });
        setWhatIfResult(wi);
      } catch (e: any) {
        setPlannerError(e?.message || 'Failed to compute planner');
      } finally {
        setPlannerLoading(false);
      }
    })();
  }, [selectedVariant, tabValue]);

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
            </>
          )}
        </>
      )}
    </Container>
  );
};

export default Dashboard;