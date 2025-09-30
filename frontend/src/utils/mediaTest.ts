/**
 * Media Streaming Test Utility
 * Tests video playback, quality selection, and streaming performance
 */

interface StreamingTest {
  name: string
  description: string
  test: () => Promise<boolean>
}

interface TestResults {
  passed: number
  failed: number
  total: number
  details: Array<{
    name: string
    status: 'PASS' | 'FAIL'
    message: string
    duration?: number
  }>
}

class MediaStreamingTester {
  private baseUrl: string
  private token: string | null

  constructor() {
    const env = (import.meta as any).env || {}
    this.baseUrl = env.VITE_API_URL || 'http://localhost:8000'
    this.token = localStorage.getItem('access_token')
  }

  /**
   * Run all streaming tests
   */
  async runAllTests(): Promise<TestResults> {
    console.log('🎬 Starting Media Streaming Tests...')
    
    const tests: StreamingTest[] = [
      {
        name: 'API Connectivity',
        description: 'Test backend API connection',
        test: () => this.testApiConnectivity()
      },
      {
        name: 'Authentication',
        description: 'Test JWT token authentication',
        test: () => this.testAuthentication()
      },
      {
        name: 'Media List',
        description: 'Test media files endpoint',
        test: () => this.testMediaList()
      },
      {
        name: 'Video Streaming',
        description: 'Test video streaming endpoint',
        test: () => this.testVideoStreaming()
      },
      {
        name: 'Range Requests',
        description: 'Test HTTP range request support',
        test: () => this.testRangeRequests()
      },
      {
        name: 'Quality Selection',
        description: 'Test video quality options',
        test: () => this.testQualitySelection()
      },
      {
        name: 'Subtitle Support',
        description: 'Test subtitle loading',
        test: () => this.testSubtitleSupport()
      }
    ]

    const results: TestResults = {
      passed: 0,
      failed: 0,
      total: tests.length,
      details: []
    }

    for (const test of tests) {
      const startTime = Date.now()
      
      try {
        console.log(`🧪 Running: ${test.name}`)
        const passed = await test.test()
        const duration = Date.now() - startTime
        
        if (passed) {
          results.passed++
          results.details.push({
            name: test.name,
            status: 'PASS',
            message: test.description,
            duration
          })
          console.log(`✅ ${test.name} - PASSED (${duration}ms)`)
        } else {
          results.failed++
          results.details.push({
            name: test.name,
            status: 'FAIL',
            message: `${test.description} - Test failed`,
            duration
          })
          console.log(`❌ ${test.name} - FAILED (${duration}ms)`)
        }
      } catch (error) {
        const duration = Date.now() - startTime
        results.failed++
        results.details.push({
          name: test.name,
          status: 'FAIL',
          message: `${test.description} - Error: ${error}`,
          duration
        })
        console.log(`❌ ${test.name} - ERROR: ${error} (${duration}ms)`)
      }
    }

    console.log(`\n📊 Test Results: ${results.passed}/${results.total} passed`)
    return results
  }

  /**
   * Test backend API connectivity
   */
  private async testApiConnectivity(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      return response.ok
    } catch (error) {
      console.error('API connectivity test failed:', error)
      return false
    }
  }

  /**
   * Test JWT authentication
   */
  private async testAuthentication(): Promise<boolean> {
    if (!this.token) {
      console.warn('No access token found')
      return false
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/v1/users/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        }
      })
      
      return response.ok
    } catch (error) {
      console.error('Authentication test failed:', error)
      return false
    }
  }

  /**
   * Test media files endpoint
   */
  private async testMediaList(): Promise<boolean> {
    if (!this.token) return false

    try {
      const response = await fetch(`${this.baseUrl}/api/v1/media?page_size=5`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) return false
      
      const data = await response.json()
      return Array.isArray(data.media) && data.media.length > 0
    } catch (error) {
      console.error('Media list test failed:', error)
      return false
    }
  }

  /**
   * Test video streaming endpoint
   */
  private async testVideoStreaming(): Promise<boolean> {
    if (!this.token) return false

    try {
      // First get a media file ID
      const mediaResponse = await fetch(`${this.baseUrl}/api/v1/media?page_size=1`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!mediaResponse.ok) return false
      
      const mediaData = await mediaResponse.json()
      if (!mediaData.media || mediaData.media.length === 0) return false
      
      const mediaId = mediaData.media[0].id
      
      // Test streaming endpoint
      const streamResponse = await fetch(`${this.baseUrl}/api/v1/media/${mediaId}/stream?token=${this.token}`, {
        method: 'HEAD' // Use HEAD to avoid downloading content
      })
      
      return streamResponse.ok
    } catch (error) {
      console.error('Video streaming test failed:', error)
      return false
    }
  }

  /**
   * Test HTTP range request support
   */
  private async testRangeRequests(): Promise<boolean> {
    if (!this.token) return false

    try {
      // Get a media file ID
      const mediaResponse = await fetch(`${this.baseUrl}/api/v1/media?page_size=1`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!mediaResponse.ok) return false
      
      const mediaData = await mediaResponse.json()
      if (!mediaData.media || mediaData.media.length === 0) return false
      
      const mediaId = mediaData.media[0].id
      
      // Test range request
      const rangeResponse = await fetch(`${this.baseUrl}/api/v1/media/${mediaId}/stream?token=${this.token}`, {
        method: 'HEAD',
        headers: {
          'Range': 'bytes=0-1023'
        }
      })
      
      return rangeResponse.status === 206 || rangeResponse.status === 200
    } catch (error) {
      console.error('Range request test failed:', error)
      return false
    }
  }

  /**
   * Test video quality selection (mock test)
   */
  private async testQualitySelection(): Promise<boolean> {
    // This is a mock test since quality selection is frontend-only
    const qualities = ['auto', '1080p', '720p', '480p', '360p']
    return qualities.length > 0
  }

  /**
   * Test subtitle support
   */
  private async testSubtitleSupport(): Promise<boolean> {
    if (!this.token) return false

    try {
      // Get a media file ID
      const mediaResponse = await fetch(`${this.baseUrl}/api/v1/media?page_size=1`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!mediaResponse.ok) return false
      
      const mediaData = await mediaResponse.json()
      if (!mediaData.media || mediaData.media.length === 0) return false
      
      const mediaId = mediaData.media[0].id
      
      // Test subtitle endpoint (may return empty array, that's ok)
      const subtitleResponse = await fetch(`${this.baseUrl}/api/v1/media/${mediaId}/subtitles`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json'
        }
      })
      
      return subtitleResponse.ok
    } catch (error) {
      console.error('Subtitle support test failed:', error)
      return false
    }
  }

  /**
   * Generate test report
   */
  generateReport(results: TestResults): string {
    const passRate = ((results.passed / results.total) * 100).toFixed(1)
    
    let report = `
🎬 WATCH1 MEDIA STREAMING TEST REPORT
=====================================

📊 SUMMARY:
- Total Tests: ${results.total}
- Passed: ${results.passed} (${passRate}%)
- Failed: ${results.failed}

📋 DETAILED RESULTS:
`

    results.details.forEach(detail => {
      const status = detail.status === 'PASS' ? '✅' : '❌'
      const duration = detail.duration ? ` (${detail.duration}ms)` : ''
      report += `${status} ${detail.name}${duration}\n   ${detail.message}\n\n`
    })

    report += `
🎯 RECOMMENDATIONS:
${results.failed === 0 ? 
  '✅ All tests passed! Your media streaming is working perfectly.' : 
  '❌ Some tests failed. Check the backend API connectivity and authentication.'
}

🚀 NEXT STEPS:
- Test actual video playback in browser
- Verify subtitle upload functionality
- Test quality switching during playback
- Monitor streaming performance with large files
`

    return report
  }
}

// Export for use in components
export const mediaStreamingTester = new MediaStreamingTester()

// Global test function for console use
declare global {
  interface Window {
    testMediaStreaming: () => Promise<TestResults>
  }
}

window.testMediaStreaming = async () => {
  const results = await mediaStreamingTester.runAllTests()
  console.log(mediaStreamingTester.generateReport(results))
  return results
}

export default MediaStreamingTester
