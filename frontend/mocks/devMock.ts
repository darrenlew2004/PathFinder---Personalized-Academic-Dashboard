import { api } from '../services/api';

const nowIso = () => new Date().toISOString();

export function installDevMocks() {
  // Keep originals
  const originalGet = (api as any).get.bind(api);
  const originalPost = (api as any).post.bind(api);

  // Mock GET /api/students/current
  (api as any).get = async (url: string, ...rest: any[]) => {
    const u = String(url || '');
    if (u.includes('/api/students/current')) {
      return Promise.resolve({
        data: {
          student: {
            id: '00000000-0000-0000-0000-000000000000',
            studentId: 'demo-001',
            name: 'Demo Student',
            email: 'demo@student.local',
            gpa: 3.7,
            semester: 2,
          },
          currentCourses: [
            {
              course: {
                id: 'c1',
                courseCode: 'CS101',
                courseName: 'Intro to Programming',
                credits: 3,
                difficulty: 2.5,
                prerequisites: [],
                description: 'Basic programming concepts',
              },
              enrollment: {
                id: 'e1',
                studentId: 'demo-001',
                courseId: 'c1',
                semester: 2,
                grade: null,
                status: 'ENROLLED',
                attendanceRate: 0.92,
              },
              riskPrediction: {
                id: 'r1',
                studentId: 'demo-001',
                courseId: 'c1',
                riskLevel: 'LOW',
                confidence: 0.85,
                factors: { gpa: 0.7, attendance: 0.3 },
                recommendations: ['Keep studying', 'Attend labs'],
                predictedGrade: 'A',
                createdAt: nowIso(),
              }
            }
          ],
          completedCourses: 3,
          totalCredits: 9,
          averageAttendance: 0.89,
          riskDistribution: { LOW: 2, MEDIUM: 1, HIGH: 0 }
        }
      });
    }

    // For other GETs, fall back to original
    return originalGet(url, ...rest);
  };

  // Mock POST /auth/login and /auth/register to return a demo token
  (api as any).post = async (url: string, data?: any, ...rest: any[]) => {
    const u = String(url || '');
    if (u.includes('/auth/login') || u.includes('/auth/register')) {
      return Promise.resolve({ data: { token: 'demo-token', user: { id: '0000', studentId: 'demo-001', name: 'Demo Student', email: 'demo@student.local', gpa: 3.7, semester: 2 } } });
    }

    return originalPost(url, data, ...rest);
  };

  // Return an uninstall function in case we need it
  return () => {
    api.get = originalGet;
    api.post = originalPost;
  };
}

export default installDevMocks;

// Also provide a global interceptor for fetch and XHR so absolute requests are intercepted
export function installGlobalFetchAndXhrMocks() {
  if (typeof window === 'undefined') return () => {};

  const originalFetch = window.fetch;
  (window as any).__orig_fetch__ = originalFetch;

  window.fetch = async (input: RequestInfo, init?: RequestInit) => {
    const url = typeof input === 'string' ? input : input.url;
    if (String(url).includes('/api/students/current')) {
      return new Response(JSON.stringify({
        student: {
          id: '00000000-0000-0000-0000-000000000000',
          studentId: 'demo-001',
          name: 'Demo Student',
          email: 'demo@student.local',
          gpa: 3.7,
          semester: 2,
        },
        currentCourses: [],
        completedCourses: 3,
        totalCredits: 9,
        averageAttendance: 0.89,
        riskDistribution: { LOW: 2, MEDIUM: 1, HIGH: 0 }
      }), { status: 200, headers: { 'Content-Type': 'application/json' } });
    }

    return originalFetch(input, init);
  };

  // Patch XHR open/send to intercept
  const origOpen = XMLHttpRequest.prototype.open as any;
  const origSend = XMLHttpRequest.prototype.send as any;

  (XMLHttpRequest.prototype as any).open = function (method: string, url: string | URL) {
    try {
      this.__mock_url = String(url);
    } catch (e) {
      this.__mock_url = '';
    }
    return origOpen.apply(this, arguments as any);
  };

  (XMLHttpRequest.prototype as any).send = function (body?: any) {
    try {
      const url = this.__mock_url || '';
      if (url.includes('/api/students/current')) {
        // emulate successful XHR response asynchronously
        this.readyState = 4;
        this.status = 200;
        this.responseText = JSON.stringify({
          student: {
            id: '00000000-0000-0000-0000-000000000000',
            studentId: 'demo-001',
            name: 'Demo Student',
            email: 'demo@student.local',
            gpa: 3.7,
            semester: 2,
          },
          currentCourses: [],
          completedCourses: 3,
          totalCredits: 9,
          averageAttendance: 0.89,
          riskDistribution: { LOW: 2, MEDIUM: 1, HIGH: 0 }
        });

        setTimeout(() => {
          if (typeof this.onreadystatechange === 'function') this.onreadystatechange();
          if (typeof this.onload === 'function') this.onload({ target: this });
        }, 0);

        return;
      }
    } catch (e) {
      // fallthrough to original
    }

    return origSend.apply(this, arguments as any);
  };

  return () => {
    window.fetch = (window as any).__orig_fetch__ || originalFetch;
    XMLHttpRequest.prototype.open = origOpen;
    XMLHttpRequest.prototype.send = origSend;
  };
}
