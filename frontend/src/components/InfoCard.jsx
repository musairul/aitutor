import { useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'

function InfoCard({ data, onView }) {
  useEffect(() => {
    // Track when info card is viewed
    if (onView) {
      onView({
        contentLength: data.content?.length || 0,
        hasTitle: !!data.title
      })
    }
  }, [])

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title text-2xl mb-4">{data.title}</h2>
        <div className="prose max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkMath]}
            rehypePlugins={[rehypeKatex]}
          >
            {data.content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  )
}

export default InfoCard
