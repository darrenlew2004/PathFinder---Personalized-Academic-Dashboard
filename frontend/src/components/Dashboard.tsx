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
  Divider,
  Stack,
  Fade,
  Button,
  Avatar,
  TextField,
  InputAdornment,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, LineChart, Line, Area, AreaChart } from 'recharts';
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
  Dashboard as DashboardIcon,
  Timeline,
  HourglassEmpty,
  Search,
  FilterList,
} from '@mui/icons-material';
import { AppDispatch, RootState } from '../../store';
import { fetchStudentStats, fetchStudentWithSubjects } from '../../features/studentSlice';
import { ProgressResponse, getStudentProgress, getElectives, ElectivesResponse } from '../../services/catalogue';
import { getStudentAnalytics, StudentProfile } from '../../services/analytics';
import { getMultipleSubjectPredictions, StudentPredictionReport, SubjectPrediction, getRiskColor, getRiskEmoji, formatProbability } from '../../services/predictions';

const Dashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { currentStudent, studentWithSubjects, loading, error } = useSelector((state: RootState) => state.students);
  const [tabValue, setTabValue] = useState(0);
  // Planner state
  const [selectedVariant] = useState<string>('202301-normal');
  const [progress, setProgress] = useState<ProgressResponse | null>(null);
  const [electives, setElectives] = useState<ElectivesResponse | null>(null);
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
  // Course filtering state
  const [showAllCompleted, setShowAllCompleted] = useState(false);
  const [showAllPending, setShowAllPending] = useState(false);
  const [gradeFilter, setGradeFilter] = useState<string>('All');
  const [sortBy, setSortBy] = useState<string>('recent');
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    // Only fetch if we don't already have student data from login
    if (!currentStudent) {
      dispatch(fetchStudentStats());
    }
  }, [dispatch, currentStudent]);

  useEffect(() => {
    // Fetch subjects and analytics when on main dashboard
    if (tabValue === 0 && currentStudent) {
      if (!studentWithSubjects) {
        dispatch(fetchStudentWithSubjects(currentStudent.id));
      }
      if (!analyticsData) {
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
    }
    
    // Load planner data when switching to Planner tab
    if (tabValue === 1 && !progress) {
      (async () => {
        try {
          setPlannerError(null);
          setPlannerLoading(true);
          
          console.log('[Planner] Starting to load data...');
          console.log('[Planner] Current student:', currentStudent?.id);
          console.log('[Planner] Has studentWithSubjects:', !!studentWithSubjects);
          console.log('[Planner] Selected variant:', selectedVariant);
          
          // Ensure we have subjects available
          if (currentStudent && !studentWithSubjects) {
            console.log('[Planner] Fetching student subjects...');
            dispatch(fetchStudentWithSubjects(currentStudent.id));
          }
          
          console.log('[Planner] Fetching progress and electives...');
          const startTime = Date.now();
          
          // Fetch progress and electives
          const [prog, electivesData] = await Promise.all([
            getStudentProgress(
              selectedVariant.split('-')[0] || '202301', 
              selectedVariant.split('-')[1] || 'normal'
            ),
            getElectives(selectedVariant)
          ]);
          
          const loadTime = Date.now() - startTime;
          console.log(`[Planner] Data loaded in ${loadTime}ms`);
          
          setProgress(prog);
          setElectives(electivesData);
          
        } catch (e: any) {
          console.error('[Planner] Error loading data:', e);
          setPlannerError(e?.message || 'Failed to load planner. This might be due to a slow network connection or server issue.');
        } finally {
          setPlannerLoading(false);
        }
      })();
    }
  }, [tabValue, currentStudent, studentWithSubjects, dispatch, progress, selectedVariant]);

  // Function to manually load predictions (lazy loading)
  const loadPredictions = async () => {
    if (!currentStudent || !progress || !electives || predictionsLoading) return;
    
    try {
      setPredictionsLoading(true);
      console.log('[Predictions] Starting to load AI recommendations...');
      
      // Get actual elective course codes from the elective groups
      const electiveCodes = new Set<string>();
      
      // For each remaining elective placeholder, get the available course options
      const remainingPlaceholders = [
        ...progress.discipline_elective_placeholders_remaining,
        ...progress.free_elective_placeholders_remaining
      ];
      
      for (const placeholder of remainingPlaceholders) {
        const group = electives.elective_groups[placeholder];
        if (group && group.options) {
          group.options.forEach(course => {
            if (!course.is_placeholder) {
              electiveCodes.add(course.subject_code);
            }
          });
        }
      }
      
      const electiveSubjects = Array.from(electiveCodes).slice(0, 5); // Limit to 5 for faster loading
      console.log(`[Predictions] Requesting predictions for ${electiveSubjects.length} subjects:`, electiveSubjects);
      
      if (electiveSubjects.length > 0) {
        const startTime = Date.now();
        
        const report = await getMultipleSubjectPredictions(currentStudent.id, electiveSubjects);
        
        const loadTime = Date.now() - startTime;
        console.log(`[Predictions] Loaded in ${loadTime}ms`);
        
        setPredictions(report);
      } else {
        console.log('[Predictions] No eligible subjects found');
      }
    } catch (e: any) {
      console.error('[Predictions] Error loading predictions:', e);
      alert(`Failed to load AI recommendations: ${e?.message || 'Unknown error'}`);
    } finally {
      setPredictionsLoading(false);
    }
  };

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
    <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
      {/* Modern Header */}
      <Box 
        sx={{ 
          mb: 4, 
          p: 3, 
          background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 100%)',
          borderRadius: 3,
          color: 'white',
          boxShadow: '0 10px 40px rgba(15, 12, 41, 0.4)'
        }}
      >
        {/* Header removed - now shown in Overview tab */}
      </Box>

      {/* Modern Tabs */}
      <Paper 
        elevation={0} 
        sx={{ 
          mb: 3, 
          borderRadius: 3, 
          overflow: 'hidden',
          border: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          sx={{
            '& .MuiTab-root': {
              minHeight: 70,
              fontSize: '1rem',
              fontWeight: 600,
            }
          }}
        >
          <Tab 
            label="Dashboard" 
            icon={<DashboardIcon />} 
            iconPosition="start"
            sx={{ flex: 1 }}
          />
          <Tab 
            label="Academic Planner" 
            icon={<Timeline />} 
            iconPosition="start"
            sx={{ flex: 1 }}
          />
        </Tabs>
      </Paper>

      {/* Main Dashboard Tab (Overview + Courses + Analytics) */}
      {tabValue === 0 && (
        <Fade in={tabValue === 0} timeout={500}>
          <Box>
            {/* Welcome Header */}
            <Card sx={{ mb: 4, background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 100%)', color: 'white' }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2}>
                  <Avatar sx={{ width: 64, height: 64, bgcolor: 'white', color: 'primary.main', fontSize: '2rem' }}>
                    {currentStudent.name?.charAt(0) || 'S'}
                  </Avatar>
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      Welcome back, {currentStudent.name?.split(' ')[0] || 'Student'}!
                    </Typography>
                    <Typography variant="body1" sx={{ opacity: 0.9 }}>
                      {currentStudent.program || 'Student'} • Year {currentStudent.year} Sem {currentStudent.sem}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>

            {/* Stats Cards - Redesigned */}
            <Grid container spacing={3} mb={4}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography sx={{ opacity: 0.9 }} gutterBottom variant="body2">
                    Overall CGPA
                  </Typography>
                  <Typography variant="h3" fontWeight="bold">
                    {currentStudent.overallcgpa?.toFixed(2) || 'N/A'}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.8 }}>out of 4.0</Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 50, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #24243e 0%, #302b63 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography sx={{ opacity: 0.9 }} gutterBottom variant="body2">
                    Overall CAVG
                  </Typography>
                  <Typography variant="h3" fontWeight="bold">
                    {currentStudent.overallcavg?.toFixed(2) || 'N/A'}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.8 }}>average score</Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 50, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #5f2c82 0%, #49a09d 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography sx={{ opacity: 0.9 }} gutterBottom variant="body2">
                    Completed Courses
                  </Typography>
                  <Typography variant="h3" fontWeight="bold">
                    {studentWithSubjects?.subjects.filter(s => s.grade && !['P', 'EX', 'INC', 'W', '-'].includes(s.grade)).length || 0}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.8 }}>courses passed</Typography>
                </Box>
                <School sx={{ fontSize: 50, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography sx={{ opacity: 0.9 }} gutterBottom variant="body2">
                    Avg Attendance
                  </Typography>
                  <Typography variant="h3" fontWeight="bold">
                    {studentWithSubjects?.average_attendance?.toFixed(0) || 'N/A'}%
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.8 }}>attendance rate</Typography>
                </Box>
                <CalendarToday sx={{ fontSize: 50, opacity: 0.3 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Performance Overview - Charts */}
      <Grid container spacing={3} mb={4}>
        {/* Grade Distribution Pie Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                <TrendingUp sx={{ mr: 1 }} color="primary" />
                Grade Distribution
              </Typography>
              {studentWithSubjects && studentWithSubjects.subjects.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={(() => {
                        const gradeCount: Record<string, number> = {};
                        studentWithSubjects.subjects
                          .filter(s => s.grade && !['P', 'EX', 'INC', 'W', '-'].includes(s.grade))
                          .forEach(s => {
                            const grade = s.grade || 'Unknown';
                            gradeCount[grade] = (gradeCount[grade] || 0) + 1;
                          });
                        return Object.entries(gradeCount).map(([name, value]) => ({ name, value }));
                      })()}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {(() => {
                        const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d'];
                        const gradeCount: Record<string, number> = {};
                        studentWithSubjects.subjects
                          .filter(s => s.grade && !['P', 'EX', 'INC', 'W', '-'].includes(s.grade))
                          .forEach(s => {
                            const grade = s.grade || 'Unknown';
                            gradeCount[grade] = (gradeCount[grade] || 0) + 1;
                          });
                        return Object.entries(gradeCount).map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ));
                      })()}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography color="text.secondary" align="center" py={4}>No course data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Scores Bar Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                <CheckCircle sx={{ mr: 1 }} color="success" />
                Recent Course Performance
              </Typography>
              {studentWithSubjects && studentWithSubjects.subjects.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={studentWithSubjects.subjects
                      .filter(s => s.overallpercentage && s.grade && !['P', 'EX', 'INC', 'W', '-'].includes(s.grade))
                      .slice(0, 8)
                      .map(s => ({
                        name: s.subjectcode || 'N/A',
                        score: s.overallpercentage || 0,
                        fill: (s.overallpercentage || 0) >= 70 ? '#4caf50' : (s.overallpercentage || 0) >= 50 ? '#ff9800' : '#f44336'
                      }))}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                    <YAxis domain={[0, 100]} />
                    <RechartsTooltip />
                    <Bar dataKey="score" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Typography color="text.secondary" align="center" py={4}>No performance data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Student Information - Condensed */}
      <Grid container spacing={3} mb={4}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom display="flex" alignItems="center">
                <Person sx={{ mr: 1 }} />
                Personal Information
              </Typography>
              <Grid container spacing={2} mt={1}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Name</Typography>
                  <Typography variant="body1" fontWeight="medium">{currentStudent.name || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Gender</Typography>
                  <Typography variant="body1" fontWeight="medium">{currentStudent.gender || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Race</Typography>
                  <Typography variant="body1" fontWeight="medium">{currentStudent.race || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Country</Typography>
                  <Typography variant="body1" fontWeight="medium">{currentStudent.country || 'N/A'}</Typography>
                </Grid>
              </Grid>
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
              <Grid container spacing={2} mt={1}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Program</Typography>
                  <Typography variant="body1" fontWeight="medium">{currentStudent.programmecode || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Cohort</Typography>
                  <Typography variant="body1" fontWeight="medium">{currentStudent.cohort || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Status</Typography>
                  <Chip 
                    label={currentStudent.status || 'Unknown'} 
                    color={getStatusColor(currentStudent.status)}
                    size="small"
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">Graduated</Typography>
                  {currentStudent.graduated ? (
                    <Chip label="Yes" color="success" size="small" />
                  ) : (
                    <Chip label="No" color="default" size="small" />
                  )}
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

            {/* Divider between sections */}
            <Divider sx={{ my: 5 }}>
              <Chip icon={<BookOutlined />} label="Course Overview" color="primary" />
            </Divider>

            {/* Courses Section - Simplified */}
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
              {/* Completed Courses - Compact Cards with Filtering */}
              <Box mb={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2} mb={2}>
                  <Typography variant="h6" display="flex" alignItems="center">
                    <CheckCircle sx={{ mr: 1 }} color="success" />
                    Completed Courses ({studentWithSubjects.subjects.filter(s => s.grade && !['P', 'EX', 'INC', 'W', '-'].includes(s.grade)).length})
                  </Typography>
                  
                  <Box display="flex" gap={2} flexWrap="wrap">
                    {/* Search */}
                    <TextField
                      size="small"
                      placeholder="Search courses..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Search />
                          </InputAdornment>
                        ),
                      }}
                      sx={{ minWidth: 200 }}
                    />
                    
                    {/* Sort */}
                    <FormControl size="small" sx={{ minWidth: 150 }}>
                      <InputLabel>Sort By</InputLabel>
                      <Select
                        value={sortBy}
                        label="Sort By"
                        onChange={(e) => setSortBy(e.target.value)}
                      >
                        <MenuItem value="recent">Most Recent</MenuItem>
                        <MenuItem value="grade">Grade (A-F)</MenuItem>
                        <MenuItem value="score-high">Score (High-Low)</MenuItem>
                        <MenuItem value="score-low">Score (Low-High)</MenuItem>
                        <MenuItem value="name">Name (A-Z)</MenuItem>
                      </Select>
                    </FormControl>
                  </Box>
                </Box>
                
                {/* Grade Filter Chips */}
                <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
                  <Chip 
                    label="All" 
                    onClick={() => setGradeFilter('All')}
                    color={gradeFilter === 'All' ? 'primary' : 'default'}
                    variant={gradeFilter === 'All' ? 'filled' : 'outlined'}
                  />
                  {['A', 'B', 'C', 'D', 'F'].map(grade => (
                    <Chip 
                      key={grade}
                      label={grade} 
                      onClick={() => setGradeFilter(grade)}
                      color={gradeFilter === grade ? 'primary' : 'default'}
                      variant={gradeFilter === grade ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
              </Box>
              
              <Grid container spacing={2} mb={4}>
                {(() => {
                  // Filter and sort logic
                  let filteredCourses = studentWithSubjects.subjects
                    .filter(s => s.grade && !['P', 'EX', 'INC', 'W', '-'].includes(s.grade));
                  
                  // Apply search filter
                  if (searchQuery) {
                    filteredCourses = filteredCourses.filter(s => 
                      s.subjectcode?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                      s.subjectname?.toLowerCase().includes(searchQuery.toLowerCase())
                    );
                  }
                  
                  // Apply grade filter
                  if (gradeFilter !== 'All') {
                    filteredCourses = filteredCourses.filter(s => 
                      s.grade?.startsWith(gradeFilter)
                    );
                  }
                  
                  // Apply sorting
                  filteredCourses = [...filteredCourses].sort((a, b) => {
                    switch (sortBy) {
                      case 'grade':
                        return (a.grade || '').localeCompare(b.grade || '');
                      case 'score-high':
                        return (b.overallpercentage || 0) - (a.overallpercentage || 0);
                      case 'score-low':
                        return (a.overallpercentage || 0) - (b.overallpercentage || 0);
                      case 'name':
                        return (a.subjectcode || '').localeCompare(b.subjectcode || '');
                      case 'recent':
                      default:
                        // Sort by year/month descending
                        const yearA = a.examyear || 0;
                        const yearB = b.examyear || 0;
                        if (yearA !== yearB) return yearB - yearA;
                        return (b.exammonth || 0) - (a.exammonth || 0);
                    }
                  });
                  
                  // Show only first 6 unless "show all" is enabled
                  const displayCourses = showAllCompleted ? filteredCourses : filteredCourses.slice(0, 6);
                  
                  return (
                    <>
                      {displayCourses.map((subject) => (
                        <Grid item xs={12} sm={6} md={4} key={subject.id}>
                          <Card sx={{ height: '100%', '&:hover': { boxShadow: 6 }, transition: 'box-shadow 0.3s' }}>
                            <CardContent>
                              <Box display="flex" justifyContent="space-between" alignItems="start" mb={1}>
                                <Typography variant="body2" fontWeight="bold" color="primary">
                                  {subject.subjectcode}
                                </Typography>
                                <Chip 
                                  label={subject.grade} 
                                  color={getGradeColor(subject.grade)}
                                  size="small"
                                />
                              </Box>
                              <Typography variant="body2" color="text.secondary" gutterBottom noWrap>
                                {subject.subjectname || 'N/A'}
                              </Typography>
                              <Box mt={2}>
                                <Box display="flex" justifyContent="space-between" mb={0.5}>
                                  <Typography variant="caption" color="text.secondary">Score</Typography>
                                  <Typography variant="caption" fontWeight="bold">
                                    {subject.overallpercentage?.toFixed(1) || 'N/A'}%
                                  </Typography>
                                </Box>
                                <LinearProgress 
                                  variant="determinate" 
                                  value={subject.overallpercentage || 0} 
                                  sx={{ height: 6, borderRadius: 1 }}
                                  color={
                                    (subject.overallpercentage || 0) >= 70 ? 'success' :
                                    (subject.overallpercentage || 0) >= 50 ? 'warning' : 'error'
                                  }
                                />
                              </Box>
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                      
                      {/* Show More/Less Button */}
                      {filteredCourses.length > 6 && (
                        <Grid item xs={12}>
                          <Box display="flex" justifyContent="center" mt={2}>
                            <Button
                              variant="outlined"
                              onClick={() => setShowAllCompleted(!showAllCompleted)}
                              endIcon={showAllCompleted ? <ExpandLess /> : <ExpandMore />}
                            >
                              {showAllCompleted ? 'Show Less' : `Show ${filteredCourses.length - 6} More Courses`}
                            </Button>
                          </Box>
                        </Grid>
                      )}
                    </>
                  );
                })()}
              </Grid>

              {/* Pending Courses */}
              {studentWithSubjects.subjects.filter(s => !s.grade || ['P', 'EX', 'INC', 'W', '-'].includes(s.grade)).length > 0 && (
                <>
                  <Typography variant="h6" gutterBottom display="flex" alignItems="center" mb={2}>
                    <CalendarToday sx={{ mr: 1 }} color="warning" />
                    Pending / In Progress ({studentWithSubjects.subjects.filter(s => !s.grade || ['P', 'EX', 'INC', 'W', '-'].includes(s.grade)).length})
                  </Typography>
                  
                  <Grid container spacing={2}>
                    {(() => {
                      const pendingCourses = studentWithSubjects.subjects
                        .filter(s => !s.grade || ['P', 'EX', 'INC', 'W', '-'].includes(s.grade));
                      const displayPending = showAllPending ? pendingCourses : pendingCourses.slice(0, 6);
                      
                      return (
                        <>
                          {displayPending.map((subject) => (
                            <Grid item xs={12} sm={6} md={4} key={subject.id}>
                              <Card sx={{ height: '100%', borderLeft: '4px solid', borderColor: 'warning.main' }}>
                                <CardContent>
                                  <Typography variant="body2" fontWeight="bold" color="primary">
                                    {subject.subjectcode}
                                  </Typography>
                                  <Typography variant="body2" color="text.secondary" gutterBottom noWrap>
                                    {subject.subjectname || 'N/A'}
                                  </Typography>
                                  <Chip 
                                    label={subject.grade || subject.status || 'Pending'} 
                                    color="warning"
                                    size="small"
                                    sx={{ mt: 1 }}
                                  />
                                </CardContent>
                              </Card>
                            </Grid>
                          ))}
                          
                          {/* Show More/Less Button for Pending */}
                          {pendingCourses.length > 6 && (
                            <Grid item xs={12}>
                              <Box display="flex" justifyContent="center" mt={2}>
                                <Button
                                  variant="outlined"
                                  color="warning"
                                  onClick={() => setShowAllPending(!showAllPending)}
                                  endIcon={showAllPending ? <ExpandLess /> : <ExpandMore />}
                                >
                                  {showAllPending ? 'Show Less' : `Show ${pendingCourses.length - 6} More Courses`}
                                </Button>
                              </Box>
                            </Grid>
                          )}
                        </>
                      );
                    })()}
                  </Grid>
                </>
              )}
            </>
          )}
            
            {/* Divider between sections */}
            <Divider sx={{ my: 5 }}>
              <Chip icon={<Analytics />} label="Performance Analytics" color="secondary" />
            </Divider>

            {/* Analytics Section */}
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
                    <Card sx={{ 
                      height: '100%',
                      background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 100%)',
                      color: 'white'
                    }}>
                      <CardContent>
                        <Typography variant="body2" gutterBottom sx={{ opacity: 0.9 }}>
                          Current GPA
                        </Typography>
                        <Typography variant="h3" fontWeight="bold">
                          {analyticsData.current_gpa?.toFixed(2) || 'N/A'}
                        </Typography>
                        <Typography variant="caption" sx={{ opacity: 0.8 }}>
                          out of 4.0
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ 
                      height: '100%',
                      background: 'linear-gradient(135deg, #24243e 0%, #302b63 100%)',
                      color: 'white'
                    }}>
                      <CardContent>
                        <Typography variant="body2" gutterBottom sx={{ opacity: 0.9 }}>
                          Average Score
                        </Typography>
                        <Typography variant="h3" fontWeight="bold">
                          {analyticsData.avg_score?.toFixed(1) || 'N/A'}%
                        </Typography>
                        <Typography variant="caption" sx={{ opacity: 0.8 }}>
                          ± {analyticsData.score_std?.toFixed(1) || '0'} std dev
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ 
                      height: '100%',
                      background: 'linear-gradient(135deg, #5f2c82 0%, #49a09d 100%)',
                      color: 'white'
                    }}>
                      <CardContent>
                        <Typography variant="body2" gutterBottom sx={{ opacity: 0.9 }}>
                          Subjects Completed
                        </Typography>
                        <Typography variant="h3" fontWeight="bold">
                          {analyticsData.subjects_taken}
                        </Typography>
                        <Typography variant="caption" sx={{ opacity: 0.8 }}>
                          across {analyticsData.terms_taken} terms
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Card sx={{ 
                      height: '100%',
                      background: analyticsData.score_trend_per_term && analyticsData.score_trend_per_term > 0 
                        ? 'linear-gradient(135deg, #5f2c82 0%, #49a09d 100%)'
                        : 'linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%)',
                      color: 'white'
                    }}>
                      <CardContent>
                        <Typography variant="body2" gutterBottom sx={{ opacity: 0.9 }}>
                          Score Trend
                        </Typography>
                        <Typography variant="h3" fontWeight="bold">
                          {analyticsData.score_trend_per_term ? (analyticsData.score_trend_per_term > 0 ? '+' : '') + analyticsData.score_trend_per_term.toFixed(1) : 'N/A'}
                        </Typography>
                        <Typography variant="caption" sx={{ opacity: 0.8 }}>
                          % per term
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {/* Best/Worst Subjects */}
                <Grid container spacing={3} mb={4}>
                  <Grid item xs={12} md={6}>
                    <Card sx={{ height: '100%', borderTop: 4, borderColor: 'success.main' }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom color="success.main" fontWeight="bold">
                          🏆 Best Performance
                        </Typography>
                        {analyticsData.best_subject ? (
                          <>
                            <Typography variant="h6" fontWeight="bold" sx={{ mt: 2 }}>
                              {analyticsData.best_subject.subjectname}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                              {analyticsData.best_subject.subjectcode}
                            </Typography>
                            <Box sx={{ mt: 2, display: 'flex', alignItems: 'baseline', gap: 1 }}>
                              <Typography variant="h3" fontWeight="bold" color="success.main">
                                {analyticsData.best_subject.overallpercentage?.toFixed(1)}
                              </Typography>
                              <Typography variant="h5" color="text.secondary">%</Typography>
                            </Box>
                          </>
                        ) : (
                          <Typography color="text.secondary">No data</Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Card sx={{ height: '100%', borderTop: 4, borderColor: 'warning.main' }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom color="warning.main" fontWeight="bold">
                          📚 Focus Area
                        </Typography>
                        {analyticsData.worst_subject ? (
                          <>
                            <Typography variant="h6" fontWeight="bold" sx={{ mt: 2 }}>
                              {analyticsData.worst_subject.subjectname}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                              {analyticsData.worst_subject.subjectcode}
                            </Typography>
                            <Box sx={{ mt: 2, display: 'flex', alignItems: 'baseline', gap: 1 }}>
                              <Typography variant="h3" fontWeight="bold" color="warning.main">
                                {analyticsData.worst_subject.overallpercentage?.toFixed(1)}
                              </Typography>
                              <Typography variant="h5" color="text.secondary">%</Typography>
                            </Box>
                          </>
                        ) : (
                          <Typography color="text.secondary">No data</Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                {/* Term Performance */}
                <Card sx={{ borderRadius: 3 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom fontWeight="bold">
                      📊 Performance by Term
                    </Typography>
                    <TableContainer>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell><strong>Term</strong></TableCell>
                            <TableCell align="right"><strong>Avg Score</strong></TableCell>
                            <TableCell align="right"><strong>Exams</strong></TableCell>
                            <TableCell align="right"><strong>Pass Rate</strong></TableCell>
                            <TableCell><strong>Progress</strong></TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {analyticsData.term_stats.map((term) => (
                            <TableRow key={term.term} hover>
                              <TableCell><strong>{term.term}</strong></TableCell>
                              <TableCell align="right">
                                <Typography variant="body2" fontWeight="bold">
                                  {term.avg_percentage?.toFixed(1) || 'N/A'}%
                                </Typography>
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
                                  sx={{ height: 10, borderRadius: 5 }}
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
              <Alert severity="info">Loading analytics data...</Alert>
            )}
          </Box>
        </Fade>
      )}

      {/* Academic Planner Tab */}
      {tabValue === 1 && (
        <Fade in={tabValue === 1} timeout={500}>
          <Box>
          {plannerLoading ? (
            <Box 
              display="flex" 
              flexDirection="column"
              justifyContent="center" 
              alignItems="center" 
              minHeight="400px"
              sx={{
                background: 'linear-gradient(135deg, #0f0c2922 0%, #302b6322 100%)',
                borderRadius: 3,
                p: 4
              }}
            >
              <HourglassEmpty 
                sx={{ 
                  fontSize: 80, 
                  color: 'primary.main',
                  mb: 2,
                  animation: 'pulse 1.5s ease-in-out infinite',
                  '@keyframes pulse': {
                    '0%, 100%': { opacity: 1 },
                    '50%': { opacity: 0.5 }
                  }
                }} 
              />
              <Typography variant="h5" fontWeight="bold" gutterBottom>
                Calculating Your Academic Plan
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
                Please wait while we analyze your progress and generate recommendations...
              </Typography>
              <CircularProgress size={40} />
            </Box>
          ) : plannerError ? (
            <Alert severity="error">{plannerError}</Alert>
          ) : progress ? (
            <>
              {/* MAIN SPOTLIGHT: Risk Overview (AI-Powered Subject Predictions) */}
              <Card 
                sx={{ 
                  mb: 4,
                  borderRadius: 3,
                  background: 'linear-gradient(135deg, #0f0c2911 0%, #302b6311 100%)',
                  border: '2px solid',
                  borderColor: '#302b63',
                  boxShadow: '0 8px 32px rgba(15, 12, 41, 0.3)'
                }}
              >
                <CardContent sx={{ p: 4 }}>
                  <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Warning sx={{ fontSize: 36, color: 'warning.main' }} />
                      <Typography variant="h4" fontWeight="bold">
                        📊 Risk Overview
                      </Typography>
                      <Tooltip title="AI-powered success predictions for elective subjects based on your performance">
                        <Info fontSize="small" color="action" />
                      </Tooltip>
                    </Box>
                    {!predictions && !predictionsLoading && (
                      <Button
                        variant="contained"
                        color="primary"
                        size="large"
                        startIcon={<TrendingUp />}
                        onClick={loadPredictions}
                        sx={{
                          borderRadius: 2,
                          textTransform: 'none',
                          px: 4,
                          py: 1.5,
                          background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 100%)',
                          fontSize: '1.1rem',
                          fontWeight: 'bold'
                        }}
                      >
                        Load AI Risk Analysis
                      </Button>
                    )}
                  </Box>
                  
                  {!predictions && !predictionsLoading ? (
                    <Box 
                      textAlign="center" 
                      py={8}
                      sx={{
                        background: 'linear-gradient(135deg, #0f202711 0%, #2c536411 100%)',
                        borderRadius: 2,
                        border: '2px dashed',
                        borderColor: 'primary.main'
                      }}
                    >
                      <TrendingUp sx={{ fontSize: 80, color: 'primary.main', mb: 2, opacity: 0.5 }} />
                      <Typography variant="h5" color="text.secondary" gutterBottom fontWeight="bold">
                        Get AI-Powered Risk Analysis
                      </Typography>
                      <Typography variant="body1" color="text.secondary" mb={3}>
                        Click the button above to analyze your academic history and get personalized subject risk assessments
                      </Typography>
                    </Box>
                  ) : predictionsLoading ? (
                    <Box 
                      display="flex" 
                      flexDirection="column"
                      justifyContent="center" 
                      alignItems="center"
                      py={8}
                    >
                      <CircularProgress size={56} sx={{ mb: 2 }} />
                      <Typography variant="h6" color="text.secondary">
                        Analyzing your academic performance with AI...
                      </Typography>
                    </Box>
                  ) : predictions && predictions.predictions.length > 0 ? (
                    <>
                      {predictions.high_risk_subjects.length > 0 && (
                        <Alert severity="warning" sx={{ mb: 3, fontSize: '1rem' }}>
                          <strong>⚠️ Attention needed:</strong> {predictions.high_risk_subjects.length} subject(s) may be challenging based on your prerequisite performance.
                        </Alert>
                      )}
                      
                      <TableContainer component={Paper} variant="outlined" sx={{ boxShadow: 2 }}>
                        <Table size="small">
                          <TableHead>
                            <TableRow sx={{ bgcolor: 'primary.main' }}>
                              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Subject</TableCell>
                              <TableCell align="center" sx={{ color: 'white', fontWeight: 'bold' }}>Risk Level</TableCell>
                              <TableCell align="center" sx={{ color: 'white', fontWeight: 'bold' }}>Success Probability</TableCell>
                              <TableCell align="center" sx={{ color: 'white', fontWeight: 'bold' }}>Prereq GPA</TableCell>
                              <TableCell sx={{ color: 'white' }}></TableCell>
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
                                      <Box display="flex" alignItems="center" gap={1}>
                                        <Typography variant="body2" fontWeight="medium">
                                          {pred.subject_code}
                                        </Typography>
                                        {pred.prediction_method === 'hybrid' && (
                                          <Chip 
                                            label="🤖 AI" 
                                            size="small" 
                                            sx={{ height: 20, fontSize: '0.65rem' }}
                                            color="info"
                                          />
                                        )}
                                      </Box>
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
                                        
                                        {pred.ml_probability !== null && pred.ml_probability !== undefined && (
                                          <Box mt={2} p={1.5} sx={{ bgcolor: 'info.lighter', borderRadius: 1, border: '1px solid', borderColor: 'info.light' }}>
                                            <Typography variant="caption" fontWeight="bold" color="info.dark" display="flex" alignItems="center" gap={0.5}>
                                              🤖 Machine Learning Analysis
                                            </Typography>
                                            <Box mt={1} display="flex" gap={2} flexWrap="wrap">
                                              <Box>
                                                <Typography variant="caption" color="text.secondary" display="block">
                                                  ML Probability
                                                </Typography>
                                                <Typography variant="body2" fontWeight="bold" color="info.dark">
                                                  {(pred.ml_probability * 100).toFixed(1)}%
                                                </Typography>
                                              </Box>
                                              {pred.ml_confidence !== null && pred.ml_confidence !== undefined && (
                                                <Box>
                                                  <Typography variant="caption" color="text.secondary" display="block">
                                                    Confidence
                                                  </Typography>
                                                  <Typography variant="body2" fontWeight="bold" color="info.dark">
                                                    {(pred.ml_confidence * 100).toFixed(0)}%
                                                  </Typography>
                                                </Box>
                                              )}
                                            </Box>
                                            {pred.ml_top_factors && pred.ml_top_factors.length > 0 && (
                                              <Box mt={1}>
                                                <Typography variant="caption" color="text.secondary" display="block" mb={0.5}>
                                                  Top Contributing Factors:
                                                </Typography>
                                                <Box display="flex" flexWrap="wrap" gap={0.5}>
                                                  {pred.ml_top_factors.slice(0, 5).map(([factor, _], idx) => (
                                                    <Chip
                                                      key={idx}
                                                      label={`${idx + 1}. ${factor}`}
                                                      size="small"
                                                      variant="outlined"
                                                      sx={{ fontSize: '0.7rem', height: 22 }}
                                                    />
                                                  ))}
                                                </Box>
                                              </Box>
                                            )}
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
                      No elective subjects available for prediction yet, or no prerequisite data found.
                    </Typography>
                  )}
                </CardContent>
              </Card>

              {/* Academic Progress Section */}
              <Card 
                sx={{ 
                  borderRadius: 3,
                  background: 'linear-gradient(135deg, #0f0c2911 0%, #302b6311 100%)',
                  border: '1px solid',
                  borderColor: '#302b63',
                  mb: 3
                }}
              >
                <CardContent sx={{ p: 4 }}>
                  <Box display="flex" alignItems="center" gap={2} mb={3}>
                    <DashboardIcon sx={{ fontSize: 36, color: 'primary.main' }} />
                    <Typography variant="h4" fontWeight="bold">
                      Your Academic Progress
                    </Typography>
                  </Box>

                  {/* Progress Bar */}
                  <Box mb={4}>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                      <Typography variant="h6" color="text.secondary">
                        Overall Completion
                      </Typography>
                      <Typography variant="h4" fontWeight="bold" color="primary.main">
                        {progress.percent_complete.toFixed(1)}%
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={progress.percent_complete} 
                      sx={{ 
                        height: 16, 
                        borderRadius: 2,
                        backgroundColor: 'rgba(0,0,0,0.1)',
                        '& .MuiLinearProgress-bar': {
                          borderRadius: 2,
                          background: 'linear-gradient(90deg, #0f0c29 0%, #302b63 100%)'
                        }
                      }} 
                    />
                    <Box display="flex" justifyContent="space-between" mt={1}>
                      <Typography variant="body2" color="text.secondary">
                        {progress.completed_credits} credits completed
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {progress.total_credits} total credits
                      </Typography>
                    </Box>
                  </Box>

                  {/* Credits Grid */}
                  <Grid container spacing={3} mb={3}>
                    <Grid item xs={12} md={4}>
                      <Paper 
                        elevation={0} 
                        sx={{ 
                          p: 3, 
                          borderRadius: 2, 
                          background: 'linear-gradient(135deg, #0f0c29 0%, #302b63 100%)',
                          color: 'white',
                          textAlign: 'center'
                        }}
                      >
                        <CheckCircle sx={{ fontSize: 48, mb: 1, opacity: 0.9 }} />
                        <Typography variant="h3" fontWeight="bold">
                          {progress.completed_credits}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9 }}>
                          Completed Credits
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Paper 
                        elevation={0} 
                        sx={{ 
                          p: 3, 
                          borderRadius: 2, 
                          background: 'linear-gradient(135deg, #24243e 0%, #302b63 100%)',
                          color: 'white',
                          textAlign: 'center'
                        }}
                      >
                        <HourglassEmpty sx={{ fontSize: 48, mb: 1, opacity: 0.9 }} />
                        <Typography variant="h3" fontWeight="bold">
                          {progress.outstanding_credits}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9 }}>
                          Outstanding Credits
                        </Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <Paper 
                        elevation={0} 
                        sx={{ 
                          p: 3, 
                          borderRadius: 2, 
                          background: 'linear-gradient(135deg, #5f2c82 0%, #49a09d 100%)',
                          color: 'white',
                          textAlign: 'center'
                        }}
                      >
                        <School sx={{ fontSize: 48, mb: 1, opacity: 0.9 }} />
                        <Typography variant="h3" fontWeight="bold">
                          {progress.total_credits}
                        </Typography>
                        <Typography variant="body2" sx={{ opacity: 0.9 }}>
                          Total Credits Required
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>

                  <Divider sx={{ my: 3 }} />

                  {/* Remaining Requirements */}
                  <Typography variant="h5" fontWeight="bold" mb={2}>
                    📚 Remaining Requirements
                  </Typography>

                  <Grid container spacing={2}>
                    {/* Core Subjects */}
                    {progress.core_remaining.length > 0 && (
                      <Grid item xs={12} md={6}>
                        <Paper 
                          elevation={0} 
                          sx={{ 
                            p: 3, 
                            borderRadius: 2, 
                            border: '2px solid',
                            borderColor: 'error.light',
                            backgroundColor: 'error.light',
                            color: 'error.dark'
                          }}
                        >
                          <Box display="flex" alignItems="center" gap={1} mb={2}>
                            <BookOutlined />
                            <Typography variant="h6" fontWeight="bold">
                              Core Subjects
                            </Typography>
                            <Chip 
                              label={progress.core_remaining.length} 
                              size="small" 
                              sx={{ 
                                backgroundColor: 'error.main', 
                                color: 'white',
                                fontWeight: 'bold'
                              }} 
                            />
                          </Box>
                          <Stack spacing={1}>
                            {progress.core_remaining.slice(0, 5).map((code) => (
                              <Box 
                                key={code}
                                sx={{ 
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: 1,
                                  p: 1.5,
                                  borderRadius: 1,
                                  backgroundColor: 'white'
                                }}
                              >
                                <Typography variant="body1" fontWeight="600">
                                  • {code}
                                </Typography>
                              </Box>
                            ))}
                            {progress.core_remaining.length > 5 && (
                              <Typography variant="body2" color="text.secondary" sx={{ pl: 1, pt: 1 }}>
                                ... and {progress.core_remaining.length - 5} more
                              </Typography>
                            )}
                          </Stack>
                        </Paper>
                      </Grid>
                    )}

                    {/* Discipline Electives */}
                    {progress.discipline_elective_placeholders_remaining.length > 0 && (
                      <Grid item xs={12} md={6}>
                        <Paper 
                          elevation={0} 
                          sx={{ 
                            p: 3, 
                            borderRadius: 2, 
                            border: '2px solid',
                            borderColor: 'warning.light',
                            backgroundColor: 'warning.light',
                            color: 'warning.dark'
                          }}
                        >
                          <Box display="flex" alignItems="center" gap={1} mb={2}>
                            <Analytics />
                            <Typography variant="h6" fontWeight="bold">
                              Discipline Electives
                            </Typography>
                            <Chip 
                              label={progress.discipline_elective_placeholders_remaining.length} 
                              size="small" 
                              sx={{ 
                                backgroundColor: 'warning.main', 
                                color: 'white',
                                fontWeight: 'bold'
                              }} 
                            />
                          </Box>
                          <Stack spacing={1}>
                            {progress.discipline_elective_placeholders_remaining.map((code) => (
                              <Box 
                                key={code}
                                sx={{ 
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: 1,
                                  p: 1.5,
                                  borderRadius: 1,
                                  backgroundColor: 'white'
                                }}
                              >
                                <Typography variant="body1" fontWeight="600">
                                  • {code}
                                </Typography>
                              </Box>
                            ))}
                          </Stack>
                        </Paper>
                      </Grid>
                    )}

                    {/* Free Electives */}
                    {progress.free_elective_placeholders_remaining.length > 0 && (
                      <Grid item xs={12} md={6}>
                        <Paper 
                          elevation={0} 
                          sx={{ 
                            p: 3, 
                            borderRadius: 2, 
                            border: '2px solid',
                            borderColor: 'info.light',
                            backgroundColor: 'info.light',
                            color: 'info.dark'
                          }}
                        >
                          <Box display="flex" alignItems="center" gap={1} mb={2}>
                            <School />
                            <Typography variant="h6" fontWeight="bold">
                              Free Electives
                            </Typography>
                            <Chip 
                              label={progress.free_elective_placeholders_remaining.length} 
                              size="small" 
                              sx={{ 
                                backgroundColor: 'info.main', 
                                color: 'white',
                                fontWeight: 'bold'
                              }} 
                            />
                          </Box>
                          <Stack spacing={1}>
                            {progress.free_elective_placeholders_remaining.map((code) => (
                              <Box 
                                key={code}
                                sx={{ 
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: 1,
                                  p: 1.5,
                                  borderRadius: 1,
                                  backgroundColor: 'white'
                                }}
                              >
                                <Typography variant="body1" fontWeight="600">
                                  • {code}
                                </Typography>
                              </Box>
                            ))}
                          </Stack>
                        </Paper>
                      </Grid>
                    )}
                  </Grid>

                  {/* Completion Message */}
                  {progress.core_remaining.length === 0 && 
                   progress.discipline_elective_placeholders_remaining.length === 0 && 
                   progress.free_elective_placeholders_remaining.length === 0 && (
                    <Box 
                      textAlign="center" 
                      py={4}
                      sx={{
                        background: 'linear-gradient(135deg, #5f2c8211 0%, #49a09d11 100%)',
                        borderRadius: 2,
                        mt: 2
                      }}
                    >
                      <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
                      <Typography variant="h4" fontWeight="bold" color="success.main" gutterBottom>
                        🎉 Congratulations!
                      </Typography>
                      <Typography variant="h6" color="text.secondary">
                        You've completed all degree requirements!
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </>
          ) : (
            <Box 
              textAlign="center" 
              py={10}
              sx={{
                background: 'linear-gradient(135deg, #0f0c2911 0%, #302b6311 100%)',
                borderRadius: 3,
                border: '2px dashed',
                borderColor: '#302b63'
              }}
            >
              <DashboardIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2, opacity: 0.3 }} />
              <Typography variant="h5" color="text.secondary" gutterBottom>
                Loading Academic Plan...
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Please wait while we fetch your progress data
              </Typography>
            </Box>
          )}
          </Box>
        </Fade>
      )}
    </Container>
  );
};

export default Dashboard;
